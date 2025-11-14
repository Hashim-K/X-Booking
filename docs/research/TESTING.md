# Testing Guide - Multi-Booking System

## Quick Test Commands

### Run All Tests
```bash
poetry run python test_multibooking.py
```

### Test Database Only
```bash
poetry run python -c "
from test_multibooking import test_database
test_database()
"
```

### Test Frontend Build
```bash
bun run build
```

### Test Frontend Dev Server
```bash
bun run dev
# Open http://localhost:3000
```

## Test Results Summary

### ✅ Phase 5.2 - Database Layer
- **Account Management**: CREATE, READ, UPDATE, DELETE ✓
- **Duplicate Prevention**: UNIQUE constraints enforced ✓
- **Booking Management**: Full CRUD with status tracking ✓
- **Slot Caching**: Update and retrieve availability ✓
- **Snipe Jobs**: Schedule and track automated bookings ✓
- **Audit Logging**: Complete booking attempt history ✓
- **Statistics**: Success rates and usage metrics ✓

### ✅ Phase 5.3 - Slot Monitor Service
- **Callback System**: Event notifications ✓
- **Cache Retrieval**: Get slots from database ✓
- **Consecutive Finder**: Find 3-hour sequences ✓
- **Monitor Configuration**: Poll interval and TTL ✓
- **API Routes**: All endpoints created ✓
- **React Component**: SlotGrid UI built ✓

### ✅ Build Verification
- **TypeScript Compilation**: No errors ✓
- **Next.js Build**: Successful ✓
- **API Routes**: All registered ✓

## Manual Testing

### Test Slot Scraping (Requires Credentials)
```python
from datetime import date
from src.services.slot_monitor import slot_monitor
from src.services.database import db_service

# Initialize
db_service.initialize_db()

# Scrape slots (replace with real credentials)
slots = slot_monitor.update_slot_cache(
    location='X1',
    target_date=date(2025, 11, 17),
    netid='your_netid',
    password='your_password'
)

print(f"Found {len(slots)} slots")
for slot in slots:
    status = "Available" if slot.is_available else "Full"
    print(f"  {slot.time_slot}: {status}")
```

### Test API Endpoints

#### Get Cached Slots
```bash
curl "http://localhost:3000/api/slots/available?location=X1&date=2025-11-17"
```

#### Refresh Slots (POST with credentials)
```bash
curl -X POST http://localhost:3000/api/slots/available \
  -H "Content-Type: application/json" \
  -d '{
    "location": "X1",
    "date": "2025-11-17",
    "netid": "your_netid",
    "password": "your_password"
  }'
```

#### Monitor Real-Time (SSE)
```bash
curl -N "http://localhost:3000/api/slots/monitor?locations=X1,X3&dateRange=3"
```

### Test Database Directly
```bash
# Open database with sqlite3
sqlite3 bookings.db

# View tables
.tables

# Query accounts
SELECT * FROM accounts;

# Query bookings
SELECT * FROM bookings;

# Query slot availability
SELECT * FROM slot_availability;

# Exit
.quit
```

## What's Been Tested

### Database Operations
✓ Create accounts with unique constraints  
✓ Prevent duplicate bookings for same time slot  
✓ Update booking status with references  
✓ Cache slot availability with capacity info  
✓ Schedule snipe jobs with JSON account lists  
✓ Log booking attempts with execution time  
✓ Calculate account statistics  

### Slot Monitor
✓ Register callbacks for events  
✓ Retrieve cached availability  
✓ Find consecutive hour sequences (for 3-hour bookings)  
✓ Configure poll interval and cache TTL  

### Infrastructure
✓ All API routes exist and are properly structured  
✓ React components compile without errors  
✓ TypeScript types are valid  
✓ Next.js build succeeds  

## Known Limitations

1. **Slot Scraping**: Not tested in automated suite (requires valid credentials)
2. **Background Monitoring**: Thread-based polling not tested (would run indefinitely)
3. **SSE Streaming**: Real-time updates not tested (requires live server)
4. **Sub-locations**: X1 A/B and X3 A/B dropdown interaction not yet implemented

## Next Steps

Once you're satisfied with the testing results, we can proceed with:
- **Phase 5.4**: Account Management API & UI
- **Phase 5.5**: Booking Management with Cancel
- **Phase 5.6**: APScheduler Integration
- **Phase 5.7**: Sub-location Support (ng-select)
- **Phase 5.8**: Divide & Conquer Strategy
- **Phase 5.9**: Live Dashboard
- **Phase 5.10**: Full Integration Testing

## Troubleshooting

### Database locked error
```bash
# Close all connections and delete database
rm bookings.db
poetry run python test_multibooking.py
```

### Import errors
```bash
# Ensure you're using poetry shell or poetry run
poetry install
poetry run python test_multibooking.py
```

### Next.js build errors
```bash
# Clean and rebuild
rm -rf .next
bun run build
```
