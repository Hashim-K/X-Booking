import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

/**
 * GET /api/accounts
 * List all accounts or filter by active status
 * 
 * Query params:
 * - isActive: 'true' | 'false' (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const isActive = searchParams.get('isActive');

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'get_accounts',
        is_active: isActive ? isActive === 'true' : undefined,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to fetch accounts' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      accounts: data.accounts,
      count: data.accounts.length,
    });
  } catch (error) {
    console.error('Error fetching accounts:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/accounts
 * Create a new account
 * 
 * Body:
 * - netid: string (required)
 * - password: string (required)
 * - isActive: boolean (optional, default: true)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { netid, password, isActive = true } = body;

    if (!netid || !password) {
      return NextResponse.json(
        { error: 'netid and password are required' },
        { status: 400 }
      );
    }

    // Validate netid format (basic validation)
    if (netid.length < 3 || netid.length > 100) {
      return NextResponse.json(
        { error: 'netid must be between 3 and 100 characters' },
        { status: 400 }
      );
    }

    // Call Python backend
    const response = await fetch('http://localhost:8008/api/python/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_account',
        netid,
        password,
        is_active: isActive,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to create account' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      message: 'Account created successfully',
      account: data.account,
    }, { status: 201 });
  } catch (error) {
    console.error('Error creating account:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
