import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * GET /api/accounts/[id]/bookings
 * Get all bookings for a specific account
 * 
 * Query params:
 * - date: 'YYYY-MM-DD' (optional)
 * - status: 'pending' | 'confirmed' | 'failed' | 'cancelled' (optional)
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const accountId = parseInt(id);

    if (isNaN(accountId)) {
      return NextResponse.json(
        { error: 'Invalid account ID' },
        { status: 400 }
      );
    }

    const searchParams = request.nextUrl.searchParams;
    const date = searchParams.get('date');
    const status = searchParams.get('status');

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'get_account_bookings',
        account_id: accountId,
        date,
        status,
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
    console.error('Error fetching account bookings:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
