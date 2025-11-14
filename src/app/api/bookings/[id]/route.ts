import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * GET /api/bookings/[id]
 * Get a specific booking by ID
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const bookingId = parseInt(id);

    if (isNaN(bookingId)) {
      return NextResponse.json(
        { error: 'Invalid booking ID' },
        { status: 400 }
      );
    }

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'get_booking',
        booking_id: bookingId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Booking not found' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      booking: data.booking,
    });
  } catch (error) {
    console.error('Error fetching booking:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/bookings/[id]
 * Cancel a booking
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const bookingId = parseInt(id);

    if (isNaN(bookingId)) {
      return NextResponse.json(
        { error: 'Invalid booking ID' },
        { status: 400 }
      );
    }

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'cancel_booking',
        booking_id: bookingId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to cancel booking' },
        { status: response.status }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Booking cancelled successfully',
    });
  } catch (error) {
    console.error('Error cancelling booking:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/bookings/[id]
 * Update a booking (mainly for status updates)
 * 
 * Body:
 * - status: 'pending' | 'confirmed' | 'failed' | 'cancelled' (optional)
 * - bookingReference: string (optional)
 * - errorMessage: string (optional)
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const bookingId = parseInt(id);

    if (isNaN(bookingId)) {
      return NextResponse.json(
        { error: 'Invalid booking ID' },
        { status: 400 }
      );
    }

    const body = await request.json();
    const { status, bookingReference, errorMessage } = body;

    if (!status && !bookingReference && !errorMessage) {
      return NextResponse.json(
        { error: 'No fields to update' },
        { status: 400 }
      );
    }

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_booking',
        booking_id: bookingId,
        status,
        booking_reference: bookingReference,
        error_message: errorMessage,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to update booking' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      message: 'Booking updated successfully',
      booking: data.booking,
    });
  } catch (error) {
    console.error('Error updating booking:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
