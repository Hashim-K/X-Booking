# Booking Client Testing

## Overview
This module provides direct integration with the TU Delft X booking system.

## Features Implemented

### 1. **Login with Account Credentials**
```python
from src.services.booking_client import BookingClient

client = BookingClient()
result = client.login("your.email@example.com", "your_password")

if result["success"]:
    print(f"Logged in as: {result['user']['name']}")
```

### 2. **View Available Slots**
Check available booking slots for Fitness, X1, or X3:

```python
# Fitness slots for tomorrow
slots = client.get_available_slots("Fitness", "2025-11-15")

# X1-A slots (with sub-location)
slots = client.get_available_slots("X1", "2025-11-21", sub_location="A")

# X3-B slots
slots = client.get_available_slots("X3", "2025-11-21", sub_location="B")
```

### 3. **View Current Bookings**
Get all confirmed bookings for the logged-in account:

```python
bookings = client.get_current_bookings()

for booking in bookings["bookings"]:
    print(f"Date: {booking['date']} at {booking['start_time']}")
    print(f"Location: {booking['location']} {booking.get('sub_location', '')}")
    print(f"Can Cancel: {booking['can_cancel']}")
```

### 4. **Cancel a Booking**
Cancel a specific booking by its ID:

```python
result = client.cancel_booking("1475962")

if result["success"]:
    print("Booking cancelled successfully!")
```

### 5. **Create a Booking** (Bonus)
Book an available slot:

```python
result = client.create_booking(
    location="Fitness",
    date="2025-11-15",
    time_slot="06:00",
    slot_id="...",  # From available slots
    resource_id="..."  # From available slots
)
```

## Testing

Run the interactive test script:

```bash
poetry run python test_booking.py
```

The test script will:
1. ✅ Login with your credentials
2. ✅ Show your current bookings
3. ✅ Display available Fitness slots for tomorrow
4. ✅ Display available X1-A slots (7 days ahead)
5. ✅ Display available X3-A slots (7 days ahead)
6. ✅ Optionally test booking cancellation
7. ✅ Logout

## API Endpoints Used

The client interacts with these X booking system endpoints:

- `POST /api/auth/login` - Authentication
- `GET /api/bookings/my-bookings` - Get user's bookings
- `GET /api/bookings/available` - Check available slots
- `POST /api/bookings` - Create new booking
- `DELETE /api/bookings/{id}` - Cancel booking
- `GET /api/auth/logout` - Logout

## Location & Resource IDs

### Product IDs
- **Fitness**: 20061
- **X1**: 20045
- **X3**: 20047

### Resource IDs (Sub-locations)
- **X1-A**: 4
- **X1-B**: 5
- **X3-A**: 16534
- **X3-B**: 16535

## Example Output

```
======================================================================
X Booking System - Test Client
======================================================================

Enter username/email: your.email@student.tudelft.nl
Enter password: ********

----------------------------------------------------------------------
1. Testing Login
----------------------------------------------------------------------
✅ Login successful!
   User: John Doe
   User ID: 12345

----------------------------------------------------------------------
2. Current Bookings
----------------------------------------------------------------------
Found 3 booking(s):

1. Booking ID: 1475962
   Date: 2025-11-15
   Time: 13:00 - 14:00
   Location: Fitness
   Can Cancel: Yes

2. Booking ID: 1611450
   Date: 2025-11-17
   Time: 12:00 - 13:00
   Location: X3 A
   Can Cancel: Yes

3. Booking ID: 1611449
   Date: 2025-11-17
   Time: 15:00 - 16:00
   Location: X1 A
   Can Cancel: Yes

----------------------------------------------------------------------
3. Available Fitness Slots (2025-11-15)
----------------------------------------------------------------------
Found 15 available slot(s):

1. 06:00-07:00: 🟢 12/46 spots (26%)
2. 07:00-08:00: 🟢 18/46 spots (39%)
3. 08:00-09:00: 🟢 22/46 spots (48%)
...
```

## Notes

- **Session Management**: The client maintains a session with cookies after login
- **Authentication**: Login is required before using other methods
- **Error Handling**: All methods return `{"success": bool, ...}` dicts
- **Rate Limiting**: Be mindful of request frequency to avoid rate limits
- **Slot Unlocking**: X1/X3 slots unlock 7 days in advance (typically at midnight)

## Integration with Database

The BookingClient can be integrated with the existing database services:

```python
from src.services.database import DatabaseService
from src.services.booking_client import BookingClient

# Get account from database
db = DatabaseService()
account = db.get_account_by_id(1)

# Use account credentials to login
client = BookingClient()
result = client.login(account["username"], account["password"])

# Sync bookings to database
if result["success"]:
    bookings = client.get_current_bookings()
    for booking in bookings["bookings"]:
        # Update database with confirmed bookings
        db.update_booking(...)
```
