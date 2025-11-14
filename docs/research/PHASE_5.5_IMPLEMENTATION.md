# Phase 5.5: Booking Management System

## Overview
Phase 5.5 implements a complete booking management system with CRUD operations, status tracking, and UI integration.

## Architecture

```
┌─────────────────┐      HTTP POST       ┌──────────────────┐      Python      ┌──────────────────┐
│   Next.js API   │ ───────────────────> │  Python Backend  │ ───────────────> │ BookingService   │
│    Routes       │  (localhost:8008)    │     Bridge       │                   │  + Database      │
│  /api/bookings  │ <─────────────────── │  /api/python/*   │ <───────────────  │                  │
└─────────────────┘      JSON Response   └──────────────────┘      Response    └──────────────────┘
```

## Components Implemented

### 1. Next.js API Routes (`src/app/api/bookings/`)

#### GET /api/bookings
- Lists all bookings with optional filters
- Query params: `accountId`, `date`, `status`, `location`
- Returns: `{ success: true, bookings: [...], count: number }`

#### POST /api/bookings
- Creates new booking(s) for specified time slots
- Body: `{ accountId, date, timeSlots[], location, subLocation?, retryInterval?, autoRetry? }`
- Creates one booking record per time slot
- Returns: `{ success: true, bookings: [...] }`

#### GET /api/bookings/[id]
- Gets a specific booking by ID
- Returns: `{ success: true, booking: {...} }`

#### PUT /api/bookings/[id]
- Updates booking status and related fields
- Body: `{ status?, bookingReference?, errorMessage? }`
- Returns: `{ success: true, booking: {...} }`

#### DELETE /api/bookings/[id]
- Cancels a booking (sets status to 'cancelled')
- Only works for 'pending' or 'confirmed' bookings
- Returns: `{ success: true, message: "..." }`

### 2. Python Booking Service (`src/services/booking_service.py`)

Complete booking management service with methods:
- `create_booking()` - Create bookings for multiple time slots
- `get_bookings()` - List with filters
- `get_booking()` - Get single booking
- `update_booking()` - Update status/reference/error
- `cancel_booking()` - Mark as cancelled
- `mark_booking_confirmed()` - Set confirmed status
- `mark_booking_failed()` - Set failed status
- `get_account_bookings()` - Get bookings for specific account
- `get_booking_logs()` - Get audit trail
- `get_upcoming_bookings()` - Future bookings only
- `get_booking_statistics()` - Aggregated stats

### 3. Python API Bridge (`src/api/booking_api.py`)

Handles HTTP requests from Next.js and routes to BookingService:
- `handle_booking_request()` - Main router
- `create_booking()` - Create handler
- `get_bookings()` - List handler  
- `get_booking()` - Get handler
- `update_booking()` - Update handler
- `cancel_booking()` - Cancel handler

Returns tuple: `(response_dict, status_code)`

### 4. UI Components

#### Single Booking Tab (Updated)
- Now calls `POST /api/bookings` instead of old `/api/book`
- Requires account selection before booking
- Shows status messages for success/error
- Validates accountId, date, and timeSlots

#### BookingHistory Component
- Fetches from `GET /api/bookings` or `GET /api/accounts/[id]/bookings`
- Supports status and date filtering
- Cancel button calls `DELETE /api/bookings/[id]`
- Auto-refreshes after cancellation
- Color-coded status badges

#### AccountSwitcher Component
- Sets `selectedAccountId` state
- Used by Single Booking tab for booking creation
- Used by BookingHistory for filtered view

## Database Schema

Bookings table includes:
- `id` - Primary key
- `account_id` - Foreign key to accounts
- `booking_date` - Date (YYYY-MM-DD)
- `time_slot` - Time (HH:MM:SS)
- `location` - 'Fitness', 'X1', or 'X3'
- `sub_location` - Optional 'A' or 'B' for X1/X3
- `status` - 'pending', 'confirmed', 'failed', 'cancelled'
- `booking_reference` - Confirmation number from system
- `error_message` - Error details if failed
- `created_at` / `updated_at` - Timestamps

## Python Backend Bridge (TODO)

### Requirements
The Next.js API routes expect to call:
```
POST http://localhost:8008/api/python/bookings
```

### Implementation Options

#### Option 1: Flask Server (Recommended)
1. Add Flask to dependencies: `poetry add flask flask-cors`
2. Create `src/api/server.py`:
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.api.booking_api import handle_booking_request

app = Flask(__name__)
CORS(app)

@app.route('/api/python/bookings', methods=['POST'])
def bookings():
    data = request.get_json()
    response, status_code = handle_booking_request(data)
    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8009, debug=True)
```

3. Run alongside Next.js dev server

#### Option 2: Integrate into main.py
Add HTTP server capabilities to main.py to handle API requests

#### Option 3: Next.js Server Actions (Alternative)
Bypass Python backend and call database directly from Next.js server actions (requires SQLite driver for Node.js)

### Current Status
- ✅ Next.js API routes created
- ✅ Python BookingService implemented
- ✅ Python API bridge handlers created
- ❌ HTTP server not yet running
- ✅ UI components updated

The system is **functionally complete** but requires the Python HTTP server to be running for end-to-end operation.

## Testing (When Backend is Running)

### 1. Create Booking via UI
1. Go to Accounts tab
2. Add/select an account
3. Go to Single Booking tab
4. Select date, location, time slots
5. Click "Start Booking"
6. Should see: "Booking created! X slot(s) added to queue."

### 2. View Booking History
1. Go to History tab
2. Should see newly created bookings with "PENDING" status
3. Filter by status/date
4. Try cancelling a booking

### 3. Via API Directly
```bash
# Create booking
curl -X POST http://localhost:3000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": 1,
    "date": "2025-11-20",
    "timeSlots": ["06:00", "07:00"],
    "location": "Fitness"
  }'

# List bookings
curl http://localhost:3000/api/bookings

# Cancel booking
curl -X DELETE http://localhost:3000/api/bookings/1
```

## Next Steps (Phase 5.6+)
- Phase 5.6: APScheduler for automated sniping at unlock times
- Phase 5.7: Sub-location support (X1-A, X1-B, X3-A, X3-B)
- Phase 5.8: Divide & Conquer multi-account strategy
- Phase 5.9: Live monitoring dashboard
- Phase 5.10: End-to-end testing & polish
