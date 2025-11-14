import { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * GET /api/slots/monitor
 * Server-Sent Events endpoint for real-time slot updates
 * 
 * Query params:
 * - locations: comma-separated list (e.g., 'X1,X3,Fitness')
 * - dateRange: number of days ahead to monitor (default: 7)
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const locationsParam = searchParams.get('locations') || 'X1,X3,Fitness';
  const dateRange = parseInt(searchParams.get('dateRange') || '7');
  
  const locations = locationsParam.split(',').filter(l => 
    ['Fitness', 'X1', 'X3'].includes(l.trim())
  );

  // Create a ReadableStream for SSE
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      // Send initial connection message
      const data = `data: ${JSON.stringify({
        type: 'connected',
        locations,
        dateRange,
        timestamp: new Date().toISOString(),
      })}\n\n`;
      controller.enqueue(encoder.encode(data));

      // Set up polling interval (every 30 seconds)
      const intervalId = setInterval(async () => {
        try {
          // Fetch latest slot data from Python backend
          const response = await fetch('http://localhost:8008/api/python/slots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'get_monitoring_updates',
              locations,
              date_range: dateRange,
            }),
          });

          if (response.ok) {
            const updates = await response.json();
            
            // Send updates via SSE
            const data = `data: ${JSON.stringify({
              type: 'slot_update',
              updates,
              timestamp: new Date().toISOString(),
            })}\n\n`;
            controller.enqueue(encoder.encode(data));
          }
        } catch (error) {
          console.error('Error fetching slot updates:', error);
          
          // Send error event
          const data = `data: ${JSON.stringify({
            type: 'error',
            message: 'Failed to fetch updates',
            timestamp: new Date().toISOString(),
          })}\n\n`;
          controller.enqueue(encoder.encode(data));
        }
      }, 30000); // Poll every 30 seconds

      // Clean up on connection close
      request.signal.addEventListener('abort', () => {
        clearInterval(intervalId);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
}
