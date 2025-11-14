# How to Find API Endpoints

The token extraction works perfectly! Now we need to find the real API endpoints.

## Quick Method (5 minutes):

1. **Open Chrome** and press `F12` to open DevTools
2. **Go to the Network tab**
3. **Navigate to** https://x.tudelft.nl and login
4. **Filter** by clicking "Fetch/XHR" to see only API calls
5. **Do these actions** and note the API endpoints:

### Action 1: View Available Slots
- Click on "Fitness" or "X1" to see available time slots
- Look for requests like:
  ```
  GET /api/bookable-product-schedule/...
  GET /api/schedule/...
  GET /api/slots/...
  ```
- Right-click the request → Copy → Copy as cURL
- Note the full URL and any query parameters

### Action 2: View Your Bookings  
- Go to "My Bookings" page
- Look for requests like:
  ```
  GET /api/bookings
  GET /api/my-bookings
  GET /api/user/bookings
  ```
- Copy the URL

### Action 3: Try to Book (DON'T CONFIRM!)
- Click on a time slot to start booking
- Look for requests like:
  ```
  POST /api/bookings
  POST /api/book
  POST /api/create-booking
  ```
- Click on the request to see the **Request Payload** (the JSON body)
- Copy both the URL and the payload structure

### Action 4: Cancel a Booking (if you have one)
- Try to cancel a booking
- Look for:
  ```
  DELETE /api/bookings/{id}
  DELETE /api/cancel/{id}
  ```

## What to Copy:

For each endpoint, copy:
1. **Method** (GET, POST, DELETE)
2. **Full URL** including path
3. **Query parameters** (the ?key=value part)
4. **Request body** (for POST requests)
5. **Response structure** (click on the "Response" tab)

## Paste Results Here:

```
AVAILABLE SLOTS:
URL: 
Method: 
Query params: 
Response sample: 

MY BOOKINGS:
URL:
Method:
Response sample:

CREATE BOOKING:
URL:
Method:
Request body:
Response sample:

CANCEL BOOKING:
URL:
Method:
Response sample:
```

Once you have these, I'll update the BookingClient_v2 with the real URLs!
