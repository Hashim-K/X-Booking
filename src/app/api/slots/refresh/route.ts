import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * POST /api/slots/refresh
 * Force refresh slot availability for specified locations and dates
 * 
 * Body:
 * - locations: string[] - Array of locations to refresh
 * - dates: string[] - Array of dates to refresh (YYYY-MM-DD)
 * - netid: string - Account for scraping
 * - password: string - Account password
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { locations, dates, netid, password } = body;

    if (!locations || !dates || !netid || !password) {
      return NextResponse.json(
        { error: 'locations, dates, netid, and password are required' },
        { status: 400 }
      );
    }

    if (!Array.isArray(locations) || !Array.isArray(dates)) {
      return NextResponse.json(
        { error: 'locations and dates must be arrays' },
        { status: 400 }
      );
    }

    // Validate locations
    const invalidLocations = locations.filter(
      l => !['Fitness', 'X1', 'X3'].includes(l)
    );
    if (invalidLocations.length > 0) {
      return NextResponse.json(
        { error: `Invalid locations: ${invalidLocations.join(', ')}` },
        { status: 400 }
      );
    }

    // Call Python backend to refresh multiple slots
    const response = await fetch('http://localhost:8008/api/python/slots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'refresh_multiple',
        locations,
        dates,
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
      results: data.results,
      total_slots: data.total_slots,
      total_available: data.total_available,
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
