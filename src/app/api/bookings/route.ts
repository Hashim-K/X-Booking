import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * GET /api/bookings
 * List all bookings with optional filters
 * 
 * Query params:
 * - accountId: number (optional)
 * - date: 'YYYY-MM-DD' (optional)
 * - status: 'pending' | 'confirmed' | 'failed' | 'cancelled' (optional)
 * - location: 'Fitness' | 'X1' | 'X3' (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const accountId = searchParams.get('accountId');
    const date = searchParams.get('date');
    const status = searchParams.get('status');
    const location = searchParams.get('location');

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'get_bookings',
        account_id: accountId ? parseInt(accountId) : undefined,
        date,
        status,
        location,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to fetch bookings' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      bookings: data.bookings,
      count: data.bookings.length,
    });
  } catch (error) {
    console.error('Error fetching bookings:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/bookings
 * Create a new booking
 * 
 * Body:
 * - accountId: number (required)
 * - date: 'YYYY-MM-DD' (required)
 * - timeSlots: string[] (required) - e.g. ['06:00', '07:00']
 * - location: 'Fitness' | 'X1' | 'X3' (required)
 * - subLocation?: string (optional) - for X1/X3: 'A' or 'B'
 * - retryInterval?: number (optional) - seconds between retries
 * - autoRetry?: boolean (optional) - whether to retry on failure
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      accountId, 
      date, 
      timeSlots, 
      location, 
      subLocation,
      retryInterval = 60,
      autoRetry = false
    } = body;

    // Validation
    if (!accountId || !date || !timeSlots || !Array.isArray(timeSlots) || timeSlots.length === 0) {
      return NextResponse.json(
        { error: 'accountId, date, and timeSlots are required' },
        { status: 400 }
      );
    }

    if (!location || !['Fitness', 'X1', 'X3'].includes(location)) {
      return NextResponse.json(
        { error: 'Invalid location. Must be Fitness, X1, or X3' },
        { status: 400 }
      );
    }

    // Validate date format
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      return NextResponse.json(
        { error: 'Invalid date format. Use YYYY-MM-DD' },
        { status: 400 }
      );
    }

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'create_booking',
        account_id: accountId,
        booking_date: date,
        time_slots: timeSlots,
        location,
        sub_location: subLocation || null,
        retry_interval: retryInterval,
        auto_retry: autoRetry,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to create booking' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      message: 'Booking created successfully',
      bookings: data.bookings, // Array of created bookings (one per time slot)
    }, { status: 201 });
  } catch (error) {
    console.error('Error creating booking:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
