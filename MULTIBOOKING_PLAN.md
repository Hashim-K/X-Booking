# Multi-Booking System - Detailed Implementation Plan

## Overview
Build a sophisticated booking management system that can automatically snipe gym slots across multiple accounts, locations, and time slots with priority-based fallback logic and real-time monitoring.

## Use Case
- **Problem**: Popular gym slots (X1, X3) get booked instantly by bots at xx:00:01
- **Solution**: Multi-account sniping system that attempts bookings across multiple accounts with priority fallback
- **Goal**: Book 3 consecutive hours (e.g., 13:00, 14:00, 15:00) at preferred location/sub-location

## System Constraints
1. **Booking Windows**:
   - X1/X3: 72 hours in advance
   - Fitness: 168 hours in advance
   - New slots unlock every hour at xx:00:00

2. **Booking Limits per Account**:
   - 1 booking per time slot per day
   - 1 booking per location/event per day
   - Each account is independent

3. **Locations**:
   - Fitness (no sub-location)
   - X1 (sub-locations: X1 A, X1 B)
   - X3 (sub-locations: X3 A, X3 B)

## Architecture Components

### 1. Database Layer (SQLite)

#### Schema:

```sql
-- Accounts table
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    netid TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- Consider encryption
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bookings table
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    booking_date DATE NOT NULL,
    time_slot TIME NOT NULL,
    location TEXT NOT NULL,  -- 'Fitness', 'X1', 'X3'
    sub_location TEXT,  -- 'X1 A', 'X1 B', 'X3 A', 'X3 B', NULL for Fitness
    status TEXT NOT NULL,  -- 'pending', 'confirmed', 'failed', 'cancelled'
    booking_reference TEXT,  -- Reference from TU Delft system
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    UNIQUE(account_id, booking_date, time_slot)  -- One booking per time slot per day per account
);

-- Slot availability cache
CREATE TABLE slot_availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    sub_location TEXT,
    booking_date DATE NOT NULL,
    time_slot TIME NOT NULL,
    is_available BOOLEAN NOT NULL,
    total_capacity INTEGER,
    remaining_capacity INTEGER,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location, sub_location, booking_date, time_slot)
);

-- Snipe jobs (scheduled booking attempts)
CREATE TABLE snipe_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_date DATE NOT NULL,
    target_time TIME NOT NULL,
    location TEXT NOT NULL,
    sub_location TEXT,
    priority INTEGER NOT NULL,
    scheduled_execution TIMESTAMP NOT NULL,  -- When to execute (xx:00:01)
    status TEXT NOT NULL,  -- 'scheduled', 'running', 'completed', 'failed'
    assigned_accounts TEXT,  -- JSON array of account IDs
    consecutive_hours INTEGER DEFAULT 1,
    time_window_start TIME,
    time_window_end TIME,
    result TEXT,  -- JSON with results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    UNIQUE(target_date, target_time, location, sub_location)
);

-- Booking history/audit log
CREATE TABLE booking_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- 'attempt', 'success', 'failure', 'cancel'
    booking_date DATE NOT NULL,
    time_slot TIME NOT NULL,
    location TEXT NOT NULL,
    sub_location TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,  -- How long the attempt took
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### 2. Backend Services

#### 2.1 Database Service (`src/services/database.py`)
```python
class DatabaseService:
    - initialize_db()
    - add_account(netid, password)
    - get_accounts(is_active=True)
    - get_account_bookings(account_id, date=None)
    - create_booking(account_id, date, time, location, sub_location)
    - update_booking_status(booking_id, status, reference=None)
    - delete_booking(booking_id)
    - can_account_book(account_id, date, time, location)
    - get_slot_availability(location, date, time_range)
    - update_slot_availability(location, sub_location, date, time, is_available, capacity)
    - create_snipe_job(target_date, target_time, location, priority, accounts, config)
    - get_pending_snipe_jobs()
    - update_snipe_job_status(job_id, status, result)
    - log_booking_attempt(account_id, action, details)
```

#### 2.2 Slot Monitor Service (`src/services/slot_monitor.py`)
```python
class SlotMonitorService:
    - start_monitoring(location, date_range)
    - stop_monitoring()
    - poll_available_slots(location, date)  # Scrapes TU Delft site
    - get_cached_availability(location, date, time_range)
    - register_callback(callback_fn)  # Notify when slots appear
```

#### 2.3 Booking Service (`src/services/booking_service.py`)
```python
class BookingService:
    - execute_single_booking(account, date, time, location, sub_location)
    - execute_priority_booking(accounts, priorities, config)
    - cancel_booking(booking_id, account)
    - validate_booking_request(account_id, date, time, location)
```

#### 2.4 Scheduler Service (`src/services/scheduler.py`)
```python
class SchedulerService:
    - schedule_snipe_job(job_config)
    - cancel_snipe_job(job_id)
    - get_upcoming_jobs()
    - execute_snipe_job(job_id)  # Runs at scheduled time
    - calculate_unlock_time(target_date, location)  # target_date - 72h/168h
```

#### 2.5 Account Manager (`src/services/account_manager.py`)
```python
class AccountManager:
    - get_available_accounts(date, time)  # Accounts that can still book
    - assign_accounts_to_job(job_id, strategy='divide_and_conquer')
    - get_account_usage_stats(date_range)
```

### 3. API Endpoints (Next.js API Routes)

#### 3.1 Account Management
```typescript
// src/app/api/accounts/route.ts
GET    /api/accounts              // List all accounts
POST   /api/accounts              // Add new account
PUT    /api/accounts/[id]         // Update account
DELETE /api/accounts/[id]         // Delete account
GET    /api/accounts/[id]/bookings // Get bookings for account
```

#### 3.2 Booking Management
```typescript
// src/app/api/bookings/route.ts
GET    /api/bookings              // List all bookings (filterable)
POST   /api/bookings              // Create manual booking
DELETE /api/bookings/[id]         // Cancel booking
GET    /api/bookings/stats        // Booking statistics
```

#### 3.3 Slot Availability
```typescript
// src/app/api/slots/route.ts
GET    /api/slots/available       // Get available slots (cached + live)
POST   /api/slots/refresh         // Force refresh slot availability
GET    /api/slots/monitor         // SSE endpoint for real-time updates
```

#### 3.4 Snipe Jobs
```typescript
// src/app/api/snipe/route.ts
GET    /api/snipe/jobs            // List scheduled snipe jobs
POST   /api/snipe/jobs            // Create new snipe job
DELETE /api/snipe/jobs/[id]       // Cancel snipe job
GET    /api/snipe/jobs/[id]/status // Get job execution status
```

#### 3.5 Active Session
```typescript
// src/app/api/session/route.ts
POST   /api/session/switch        // Switch active account
GET    /api/session/current       // Get current account
POST   /api/session/book          // Book with current account (manual)
```

### 4. Frontend Components

#### 4.1 Account Switcher Component
```typescript
// src/components/AccountSwitcher.tsx
- Dropdown showing all accounts
- Visual indicator of active account
- Show bookings count per account
- Quick stats (available slots)
```

#### 4.2 Slot Availability Grid
```typescript
// src/components/SlotGrid.tsx
- Calendar view with time slots
- Color coding: available (green), booked (red), unavailable (gray)
- Real-time updates via SSE
- Filter by location
- Click to book manually
```

#### 4.3 Booking History Table
```typescript
// src/components/BookingHistory.tsx
- List all bookings per account
- Filter by date, location, status
- Action buttons: Cancel, View Details
- Success/failure indicators
```

#### 4.4 Snipe Job Creator
```typescript
// src/components/SnipeJobForm.tsx
- Configure priority-based booking
- Set target date, time window
- Choose locations with priorities
- Assign accounts
- Schedule execution time
```

#### 4.5 Live Monitor Dashboard
```typescript
// src/components/MonitorDashboard.tsx
- Real-time slot availability
- Upcoming snipe jobs
- Recent booking attempts
- Account status overview
```

### 5. Booking Strategy: Divide & Conquer

#### Example Scenario:
**Goal**: Book X1 for 13:00, 14:00, 15:00 (3 consecutive hours)
**Available Accounts**: user1, user2, user3
**Sub-locations**: X1 A, X1 B

#### Strategy Execution:
```
At 13:00:01 (when 13:00 slot unlocks):
├─ user1 → X1 A at 13:00  (Job 1)
├─ user2 → X1 B at 13:00  (Job 2)
└─ user3 → X1 A at 13:00  (Job 3, backup)

At 14:00:01 (when 14:00 slot unlocks):
├─ If Job 1 succeeded: user1 cannot book again
├─ user2 → X1 A at 14:00  (if Job 2 succeeded)
└─ user3 → X1 B at 14:00  (if Job 3 succeeded or Job 1/2 failed)

At 15:00:01 (when 15:00 slot unlocks):
└─ Remaining account → Any available X1 slot
```

#### Fallback Logic:
```
Priority 1: X1 (any sub-location)
  ├─ Try X1 A with 2 accounts
  ├─ Try X1 B with 1 account
  └─ If all fail → Move to Priority 2

Priority 2: X3 (any sub-location)
  ├─ Try X3 A with 1 account
  ├─ Try X3 B with 1 account
  └─ If all fail → Move to Priority 3

Priority 3: Fitness (no sub-location)
  └─ Try with all remaining accounts
```

### 6. Configuration Format

#### New `bookings.json` Schema:
```json
{
  "accounts": [
    {
      "netid": "user1",
      "password": "pass1",
      "is_active": true
    },
    {
      "netid": "user2",
      "password": "pass2",
      "is_active": true
    },
    {
      "netid": "user3",
      "password": "pass3",
      "is_active": true
    }
  ],
  "snipe_config": {
    "target_date": "2025-11-17",
    "consecutive_hours": 3,
    "time_window": {
      "start": "11:00",
      "end": "18:00"
    },
    "priorities": [
      {
        "rank": 1,
        "location": "X1",
        "sub_locations": ["X1 A", "X1 B"],
        "max_accounts": 3,
        "advance_hours": 72
      },
      {
        "rank": 2,
        "location": "X3",
        "sub_locations": ["X3 A", "X3 B"],
        "max_accounts": 2,
        "advance_hours": 72
      },
      {
        "rank": 3,
        "location": "Fitness",
        "max_accounts": 3,
        "advance_hours": 168
      }
    ],
    "fallback_strategy": "accept_2_consecutive_hours"
  }
}
```

## Implementation Phases

### Phase 5.1: Foundation ✅
- [x] Basic multi-booking config structure
- [x] JSON loader and validator
- [x] Mode detection

### Phase 5.2: Database Layer (CURRENT)
- [ ] Add SQLAlchemy to dependencies
- [ ] Create database models
- [ ] Implement DatabaseService
- [ ] Create migration/initialization script
- [ ] Add database to .gitignore
- [ ] **COMMIT**: `feat: add SQLite database for booking state management`

### Phase 5.3: Slot Monitor Service
- [ ] Implement slot availability scraper
- [ ] Add caching layer for slot data
- [ ] Create SSE endpoint for real-time updates
- [ ] Add background polling task
- [ ] **COMMIT**: `feat: add live slot monitoring service`

### Phase 5.4: Account Management API
- [ ] Create account CRUD endpoints
- [ ] Add account switcher component
- [ ] Implement session management
- [ ] Add account usage statistics
- [ ] **COMMIT**: `feat: add account management API and UI`

### Phase 5.5: Booking Management
- [ ] Create booking CRUD endpoints
- [ ] Add booking history component
- [ ] Implement cancel booking functionality
- [ ] Add manual booking through UI
- [ ] **COMMIT**: `feat: add booking management with cancel support`

### Phase 5.6: Scheduler & Auto-Snipe
- [ ] Add APScheduler dependency
- [ ] Implement SchedulerService
- [ ] Create snipe job endpoints
- [ ] Add snipe job configuration UI
- [ ] Calculate and schedule unlock times
- [ ] **COMMIT**: `feat: add APScheduler for automated sniping`

### Phase 5.7: Sub-location Support (X1/X3)
- [ ] Add Angular ng-select interaction
- [ ] Update login_x() to handle sub-locations
- [ ] Add sub-location to UI components
- [ ] Test X1 A/B and X3 A/B booking
- [ ] **COMMIT**: `feat: add X1/X3 sub-location support`

### Phase 5.8: Divide & Conquer Logic
- [ ] Implement account assignment algorithm
- [ ] Add priority-based execution
- [ ] Create parallel booking coordinator
- [ ] Add result aggregation
- [ ] **COMMIT**: `feat: implement divide and conquer booking strategy`

### Phase 5.9: Live Dashboard
- [ ] Create MonitorDashboard component
- [ ] Add real-time slot grid
- [ ] Show upcoming snipe jobs
- [ ] Display booking statistics
- [ ] **COMMIT**: `feat: add live monitoring dashboard`

### Phase 5.10: Testing & Polish
- [ ] Test with 3 accounts
- [ ] Test priority fallback logic
- [ ] Test consecutive hour booking
- [ ] Verify database integrity
- [ ] Performance optimization
- [ ] **COMMIT**: `test: comprehensive multi-booking validation`

### Phase 5.11: Merge to Main
- [ ] Update main README.md
- [ ] Create migration guide
- [ ] Merge feat/multibooking → main
- [ ] Tag release v2.0.0

## Technology Stack

### Backend
- **Database**: SQLite (via SQLAlchemy)
- **Scheduler**: APScheduler
- **ORM**: SQLAlchemy
- **Validation**: Pydantic (optional)

### Frontend
- **Framework**: Next.js 15 + React 19
- **State**: React Context / Zustand
- **Real-time**: Server-Sent Events (SSE)
- **UI**: TailwindCSS + Headless UI

### New Dependencies
```toml
# pyproject.toml
[tool.poetry.dependencies]
sqlalchemy = "^2.0.0"
apscheduler = "^3.10.0"
pydantic = "^2.0.0"  # Optional for validation
```

```json
// package.json
{
  "dependencies": {
    "zustand": "^4.5.0",  // State management
    "@headlessui/react": "^1.7.0"  // UI components
  }
}
```

## Security Considerations

1. **Password Storage**: Consider encrypting account passwords in database
2. **Session Isolation**: Use separate user-data-dir for each account
3. **Rate Limiting**: Add delays between booking attempts to avoid detection
4. **Error Handling**: Graceful degradation if TU Delft changes their site
5. **Audit Trail**: Log all booking attempts for debugging

## Performance Optimization

1. **Connection Pooling**: Reuse database connections
2. **Caching**: Cache slot availability for 30-60 seconds
3. **Parallel Execution**: Use multiprocessing for simultaneous bookings
4. **Browser Reuse**: Keep browser sessions alive when possible
5. **Cleanup**: Auto-cleanup old booking logs and sessions

## Monitoring & Alerts

1. **Success Rate**: Track booking success rate per account
2. **Execution Time**: Monitor how fast bookings complete
3. **Slot Detection**: Alert when desired slots become available
4. **Job Status**: Notify on snipe job completion
5. **Error Tracking**: Log and report booking failures

## Future Enhancements (Post v2.0)

1. **Email Notifications**: Alert on successful bookings
2. **Telegram Bot**: Control bookings via Telegram
3. **ML Slot Prediction**: Predict when slots become available
4. **Multi-user Support**: Multiple users managing their own accounts
5. **Cloud Deployment**: Deploy to VPS for 24/7 operation
6. **Mobile App**: React Native app for on-the-go management

---

## Current Status

**Branch**: `feat/multibooking`  
**Phase**: 5.2 - Database Layer  
**Next Step**: Add SQLAlchemy and create database models

