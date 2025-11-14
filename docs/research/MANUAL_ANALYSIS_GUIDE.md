# Manual Network Analysis Guide

Since automated analysis is complex, here's how to manually check if the X booking system has a REST API:

## Steps:

### 1. Open Chrome DevTools
- Press F12 or right-click → Inspect
- Go to **Network** tab
- Check "Preserve log"

### 2. Login to X Booking System
- Navigate to https://x.tudelft.nl
- Login with your TU Delft credentials
- Keep Network tab open

### 3. Look for API Calls
Watch for requests that are:
- XHR or Fetch type
- Contain `/api/` in the URL
- Send/receive JSON data

### 4. Test These Actions:
a) **View Dashboard**
   - Go to https://x.tudelft.nl/bookables/fitness
   - Look for requests to load slots/bookings

b) **Click on a Time Slot**
   - Click on an available slot
   - Check what requests are made

c) **Try to Book** (don't confirm)
   - Click "Book" button
   - See if there's a POST request before confirmation
   - Cancel if you don't want to actually book

d) **View Your Bookings**
   - Go to "My Bookings" page
   - See how it loads your bookings

### 5. Analyze Key Requests

For each API-looking request, note:
- **URL**: Full endpoint path
- **Method**: GET/POST/DELETE/PUT
- **Headers**: Especially `Authorization` or cookies
- **Request Payload**: What data is sent
- **Response**: What data comes back

### 6. Export for Analysis

Right-click on an API request → Copy → Copy as cURL (bash)
Then we can convert it to Python requests!

## What We're Looking For:

### Example of a REST API (GOOD):
```
POST https://x.tudelft.nl/api/bookings
Headers: 
  Cookie: session_token=abc123
  Content-Type: application/json
Body:
  {"slot_id": 12345, "date": "2025-11-15", "time": "10:00"}
Response:
  {"success": true, "booking_id": 67890}
```

### Example of No API (BAD):
```
- No XHR/Fetch requests when booking
- Only HTML page loads
- All interactions happen client-side
- Booking state managed in Angular/React
```

## Decision Tree:

**IF** you find API endpoints:
→ ✅ We can use `requests` library!
→ Copy the cURL commands
→ I'll convert them to Python

**IF** no API endpoints found:
→ ❌ Must use Selenium
→ Keep current implementation
→ Focus on optimizing Selenium code

## Quick Test:

Run this while logged in with DevTools open:
```javascript
// Paste in Console tab:
console.log('Checking for API calls...');
performance.getEntries()
  .filter(e => e.name.includes('api') || e.name.includes('booking'))
  .forEach(e => console.log(e.name));
```

This will show if there are any API-related URLs being hit.

---

**ACTION**: Please try the manual analysis above and let me know what you find!
