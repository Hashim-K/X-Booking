# X-Booking Migration & Enhancement TODO

## Phase 1: Dependency Management Migration

### 1.1: Migrate from conda to Poetry

- [x] Create pyproject.toml with dependencies
- [x] Run `poetry install` to create virtual environment
- [x] Update .gitignore to exclude .venv and poetry.lock
- [x] Update run.sh to use Poetry
- [x] Update run.bat to use Poetry
- [x] Test: `poetry run python main.py --help`
- [x] **COMMIT**: `feat: migrate from conda to Poetry for Python dependency management`

### 1.2: Migrate from npm to Bun

- [x] Run `bun install` to install dependencies
- [x] Update .gitignore to exclude bun.lockb
- [x] Update run.sh to use Bun
- [x] Update run.bat to use Bun
- [x] Update package.json scripts if needed
- [x] Test: `bun run dev` and `bun run build`
- [x] **COMMIT**: `feat: migrate from npm to Bun for JavaScript package management`

## Phase 2: Fix React Dependencies

### 2.1: Replace react-beautiful-dnd with @dnd-kit

- [x] Install @dnd-kit packages: `bun add @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities`
- [x] Remove react-beautiful-dnd: `bun remove react-beautiful-dnd`
- [x] Rewrite TimeSelector.tsx to use @dnd-kit API
  - [x] Replace DragDropContext with DndContext
  - [x] Replace Droppable with SortableContext
  - [x] Replace Draggable with useSortable
  - [x] Update state management with arrayMove
- [x] Test drag-and-drop functionality in browser
- [x] **COMMIT**: `feat: replace react-beautiful-dnd with @dnd-kit for React 19 compatibility`

## Phase 3: Selenium & Browser Detection

### 3.1: Update Selenium driver management

- [x] Remove webdriver-manager from pyproject.toml
- [x] Remove import for webdriver_manager in main.py
- [x] Update driver initialization to use `webdriver.Chrome(options=chrome_options)`
- [x] Run `poetry lock` and `poetry install`
- [x] Test: Verify automatic ChromeDriver download works
- [x] **COMMIT**: `feat: use Selenium 4.6+ automatic driver management`

### 3.2: Implement smart browser detection

- [x] Add imports: subprocess, shutil to main.py
- [x] Create find_chrome_binary() function
- [x] Implement xdg-settings check for Linux default browser
- [x] Add fallback chain: Brave → Chrome → Chromium → Flatpak
- [x] Add macOS support: `defaults read com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers`
- [x] Add Windows support: Registry check for default browser
- [x] Update chrome_options.binary_location to use detected browser
- [x] Test on Linux with Brave/Chrome
- [x] **COMMIT**: `feat: smart cross-platform browser detection with default browser priority`

## Phase 4: Fix Booking Script

### 4.1: Update date picker selector and error handling

- [x] Update date picker CSS selector to `input[type='date'].form-control`
- [x] Add redirect wait after login: `wait.until(lambda d: 'x.tudelft.nl' in d.current_url)`
- [x] Add enhanced error logging with traceback
- [x] Add screenshot capture on error to project directory
- [x] Add HTML dump on error to project directory
- [x] Add current URL logging on error
- [x] Test: Run booking script and verify error logs
- [x] **COMMIT**: `fix: update date picker selector and add comprehensive error handling`
- [x] Add authentication check to skip login if already logged in
- [x] Check localStorage for delcom_auth to detect existing session
- [x] Test: Verify script works with and without existing session
- [x] **COMMIT**: `fix: skip login flow when user is already authenticated`
- [x] Improve success message verification with heading text check
- [x] Verify both icon and "Booking was made" heading for confirmation
- [x] **COMMIT**: `fix: enhance booking success verification with heading text check`
- [x] Add additional Chrome options for headless mode stability
- [x] Fix "session not created: unable to connect to renderer" error
- [x] Add stability options: disable-blink-features, disable-software-rasterizer, etc.
- [x] **COMMIT**: `fix: improve headless Chrome stability with additional options`
- [x] Add try-finally block for guaranteed browser cleanup on crash/error
- [x] Fix authentication check to detect login page properly (h1 + URL check)
- [x] Fix success detection to check h4 heading instead of empty icon element
- [x] Improve default browser detection with xdg-settings and .desktop mapping
- [x] Test: Verify browser cleanup, auth detection, and success detection
- [x] **COMMIT**: `feat: add robust browser cleanup and improve authentication & success detection`

### 4.2: Extend booking capabilities for X1 & X3

- [x] Add location parameter to login_x() function (default='Fitness')
- [x] Update filter logic to handle different locations:
  - [x] Fitness: tagCheckbox28 (Fitness)
  - [x] X1: tagCheckbox147
  - [x] X3: tagCheckbox149
- [x] Add location dropdown to main UI (page.tsx)
- [x] Update API route to accept location parameter
- [x] Add location selector to CLI arguments
- [x] Test: Verify argument parsing works correctly
- [x] **COMMIT**: `feat: add support for X1 and X3 fitness locations`

## Phase 5: Multi-Booking Mode

### 5.1: Implement multi-booking infrastructure

- [x] Add environment variables to .env.example:
  - [x] MULTI_BOOKING=false
  - [x] MULTI_BOOKING_FILE=./bookings.json
- [x] Create bookings.json schema example:
  ```json
  [
  	{ "netid": "user1", "password": "pass1" },
  	{ "netid": "user2", "password": "pass2" }
  ]
  ```
- [x] Add JSON credentials loader function in main.py
- [x] Add mode detection logic (single vs multi)
- [x] **COMMIT**: `feat: add multi-booking configuration structure`

### 5.2: Database Layer with SQLite

- [x] Add SQLAlchemy and Alembic to dependencies
- [x] Create database schema with 5 tables:
  - [x] `accounts` - Account credentials and status
  - [x] `bookings` - Booking records with status tracking
  - [x] `slot_availability` - Cached slot availability data
  - [x] `snipe_jobs` - Scheduled booking attempts
  - [x] `booking_log` - Audit trail
- [x] Create `src/services/database.py` with DatabaseService class
- [x] Implement all CRUD operations
- [x] Add database files to .gitignore
- [x] Write and test database functionality
- [x] **COMMIT**: `feat: add SQLite database for booking state management`

### 5.3: Slot Monitor Service

- [x] Create `src/services/slot_monitor.py`
- [x] Implement slot scraping from TU Delft website
- [x] Add caching layer (30-60 second TTL)
- [x] Create SSE endpoint for real-time updates (`/api/slots/monitor`)
- [x] Add background polling with threading
- [x] Create Next.js API routes for slot operations
- [x] Build SlotGrid component for UI
- [x] **COMMIT**: `feat: add live slot monitoring service`

### 5.4: Account Management API

- [ ] Create account CRUD endpoints in Next.js
- [ ] Add account switcher component
- [ ] Implement session management
- [ ] Add account usage statistics
- [ ] **COMMIT**: `feat: add account management API and UI`

### 5.5: Booking Management

- [ ] Create booking CRUD endpoints
- [ ] Add booking history component
- [ ] Implement cancel booking functionality
- [ ] Add manual booking through UI
- [ ] **COMMIT**: `feat: add booking management with cancel support`

### 5.6: Scheduler & Auto-Snipe

- [ ] Add APScheduler dependency
- [ ] Create `src/services/scheduler.py`
- [ ] Implement job scheduling for unlock times
- [ ] Create snipe job API endpoints
- [ ] Build snipe job configuration UI
- [ ] **COMMIT**: `feat: add APScheduler for automated sniping`

### 5.7: Sub-location Support (X1 A/B, X3 A/B)

- [ ] Research ng-select dropdown interaction
- [ ] Update login_x() to handle sub-locations
- [ ] Add sub-location to UI components
- [ ] Test all combinations
- [ ] **COMMIT**: `feat: add X1/X3 sub-location support`

### 5.8: Divide & Conquer Logic

- [ ] Implement account assignment algorithm
- [ ] Add priority-based execution
- [ ] Create parallel booking coordinator
- [ ] Add result aggregation
- [ ] **COMMIT**: `feat: implement divide and conquer booking strategy`

### 5.9: Live Dashboard

- [ ] Create MonitorDashboard component
- [ ] Add real-time slot grid
- [ ] Show upcoming snipe jobs
- [ ] Display booking statistics
- [ ] **COMMIT**: `feat: add live monitoring dashboard`

### 5.10: Testing & Polish

- [ ] Test with 3 accounts
- [ ] Test priority fallback logic
- [ ] Test consecutive hour booking
- [ ] Verify database integrity
- [ ] Performance optimization
- [ ] **COMMIT**: `test: comprehensive multi-booking validation`

### 5.11: Merge to Main

- [ ] Update main README.md
- [ ] Create migration guide
- [ ] Merge feat/multibooking → main
- [ ] Tag release v2.0.0

### OLD 5.2: Implement parallel booking with session management (SUPERSEDED BY NEW ARCHITECTURE)

- [ ] Create separate Chrome user data directories per session
- [ ] Add `--user-data-dir=/tmp/chrome_session_{netid}` to chrome_options
- [ ] Implement multiprocessing.Pool for parallel execution
- [ ] Add session-specific cookie management
- [ ] Implement progress tracking dictionary
- [ ] Add per-user error handling and result collection
- [ ] Add cleanup for temp directories after booking
- [ ] Test: Run multi-booking with 2-3 test accounts
- [ ] **COMMIT**: `feat: implement parallel multi-booking with isolated browser sessions`

### 5.3: Update UI for multi-booking mode

- [ ] Add mode toggle switch in UI (Single/Multi)
- [ ] Add file upload component for credentials JSON
- [ ] Show progress table with user status
- [ ] Display results for each user (success/failure)
- [ ] Update API route to handle multi-booking requests
- [ ] Add loading states and progress indicators
- [ ] **COMMIT**: `feat: add multi-booking mode UI with progress tracking`

## Phase 6: Docker Support

### 6.1: Create Dockerfile

- [ ] Create multi-stage Dockerfile:
  - [ ] Stage 1: Base with system dependencies
  - [ ] Stage 2: Install Bun and JS dependencies
  - [ ] Stage 3: Install Poetry and Python dependencies
  - [ ] Stage 4: Build Next.js (standalone mode)
  - [ ] Stage 5: Runtime with Chrome + all dependencies
- [ ] Install Chrome/Chromium in container
- [ ] Set up proper user permissions
- [ ] Update next.config.ts with `output: 'standalone'`
- [ ] Test: `docker build -t x-booking .`
- [ ] **COMMIT**: `feat: add multi-stage Dockerfile with Chrome support`

### 6.2: Create docker-compose.yml

- [ ] Configure environment variables passthrough
- [ ] Set up volume mounts for credentials
- [ ] Configure port mapping (8008:8008)
- [ ] Add health check endpoint
- [ ] Test: `docker-compose up -d`
- [ ] **COMMIT**: `feat: add docker-compose configuration`

### 6.3: Add Docker helper scripts

- [ ] Create docker.sh with commands:
  - [ ] up, down, restart, logs, build, clean
- [ ] Make docker.sh executable
- [ ] Create .dockerignore
- [ ] Update .env.example with Docker instructions
- [ ] Test all docker.sh commands
- [ ] **COMMIT**: `feat: add Docker management scripts and configuration`

## Phase 7: Documentation & Testing

### 7.1: Update documentation

- [ ] Update README.md:
  - [ ] Prerequisites (Python 3.10+, Poetry, Bun)
  - [ ] Installation instructions
  - [ ] Docker deployment guide
  - [ ] Multi-booking usage
  - [ ] Environment variables documentation
- [ ] Create QUICKSTART.md for fast onboarding
- [ ] Create MIGRATION.md documenting all changes
- [ ] Document multi-booking JSON format
- [ ] Add troubleshooting section
- [ ] **COMMIT**: `docs: comprehensive documentation update`

### 7.2: Final testing

- [ ] Test single booking mode (X, X1, X3)
- [ ] Test multi-booking mode with test accounts
- [ ] Test Docker deployment end-to-end
- [ ] Test on different browsers (Brave, Chrome, Chromium)
- [ ] Verify all error handling and logging
- [ ] Performance test with 5+ concurrent users
- [ ] **COMMIT**: `test: validate all functionality across modes and platforms`

---

## Current Status

**Phase**: 4.2 - Extend booking capabilities for X1 & X3 (COMPLETE)  
**Last Commit**: (pending) - feat: add support for X1 and X3 fitness locations  
**Next Step**: Test booking at all three locations and commit changes
