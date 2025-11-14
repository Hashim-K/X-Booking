import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * GET /api/slots/available
 * Get available slots for a location and date
 * 
 * Query params:
 * - location: 'Fitness' | 'X1' | 'X3'
 * - date: 'YYYY-MM-DD'
 * - timeWindowStart: 'HH:MM' (optional)
 * - timeWindowEnd: 'HH:MM' (optional)
 * - forceRefresh: 'true' | 'false' (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const location = searchParams.get('location');
    const date = searchParams.get('date');
    const timeWindowStart = searchParams.get('timeWindowStart');
    const timeWindowEnd = searchParams.get('timeWindowEnd');
    const forceRefresh = searchParams.get('forceRefresh') === 'true';

    if (!location || !date) {
      return NextResponse.json(
        { error: 'location and date are required' },
        { status: 400 }
      );
    }

    // Validate location
    if (!['Fitness', 'X1', 'X3'].includes(location)) {
      return NextResponse.json(
        { error: 'Invalid location. Must be Fitness, X1, or X3' },
        { status: 400 }
      );
    }

    // Call Python backend to get slots
    const response = await fetch('http://localhost:8008/api/python/slots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'get_cached_availability',
        location,
        date,
        time_window_start: timeWindowStart,
        time_window_end: timeWindowEnd,
        force_refresh: forceRefresh,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to fetch slots' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      location,
      date,
      slots: data.slots,
      cached: !forceRefresh,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching available slots:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/slots/available
 * Refresh slot availability for a location and date
 * 
 * Body:
 * - location: 'Fitness' | 'X1' | 'X3'
 * - date: 'YYYY-MM-DD'
 * - netid: string
 * - password: string
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { location, date, netid, password } = body;

    if (!location || !date || !netid || !password) {
      return NextResponse.json(
        { error: 'location, date, netid, and password are required' },
        { status: 400 }
      );
    }

    // Validate location
    if (!['Fitness', 'X1', 'X3'].includes(location)) {
      return NextResponse.json(
        { error: 'Invalid location. Must be Fitness, X1, or X3' },
        { status: 400 }
      );
    }

    // Call Python backend to refresh slots
    const response = await fetch('http://localhost:8008/api/python/slots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_slot_cache',
        location,
        date,
        netid,
        password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to refresh slots' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      message: 'Slots refreshed successfully',
      location,
      date,
      slots_count: data.slots_count,
      available_count: data.available_count,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error refreshing slots:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
