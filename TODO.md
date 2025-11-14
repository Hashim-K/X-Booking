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

- [ ] Add imports: subprocess, shutil to main.py
- [ ] Create find_chrome_binary() function
- [ ] Implement xdg-settings check for Linux default browser
- [ ] Add fallback chain: Brave → Chrome → Chromium → Flatpak
- [ ] Add macOS support: `defaults read com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers`
- [ ] Add Windows support: Registry check for default browser
- [ ] Update chrome_options.binary_location to use detected browser
- [ ] Test on Linux with Brave/Chrome
- [ ] **COMMIT**: `feat: smart cross-platform browser detection with default browser priority`

## Phase 4: Fix Booking Script

### 4.1: Update date picker selector and error handling

- [ ] Update date picker CSS selector to `input[type='date'].form-control`
- [ ] Add redirect wait after login: `wait.until(lambda d: 'x.tudelft.nl' in d.current_url)`
- [ ] Add enhanced error logging with traceback
- [ ] Add screenshot capture on error to project directory
- [ ] Add HTML dump on error to project directory
- [ ] Add current URL logging on error
- [ ] Test: Run booking script and verify error logs
- [ ] **COMMIT**: `fix: update date picker selector and add comprehensive error handling`

### 4.2: Extend booking capabilities for X1 & X3

- [ ] Add location parameter to login_x() function (default='X')
- [ ] Update filter logic to handle different locations:
  - [ ] X: tagCheckbox28 (Fitness)
  - [ ] X1: (find correct checkbox ID)
  - [ ] X3: (find correct checkbox ID)
- [ ] Add location dropdown to Calendar.tsx
- [ ] Update API route to accept location parameter
- [ ] Add location selector to main UI (page.tsx)
- [ ] Test booking at all three locations
- [ ] **COMMIT**: `feat: add support for X1 and X3 fitness locations`

## Phase 5: Multi-Booking Mode

### 5.1: Implement multi-booking infrastructure

- [ ] Add environment variables to .env.example:
  - [ ] MULTI_BOOKING=false
  - [ ] MULTI_BOOKING_FILE=./bookings.json
- [ ] Create bookings.json schema example:
  ```json
  [
  	{ "netid": "user1", "password": "pass1" },
  	{ "netid": "user2", "password": "pass2" }
  ]
  ```
- [ ] Add JSON credentials loader function in main.py
- [ ] Add mode detection logic (single vs multi)
- [ ] **COMMIT**: `feat: add multi-booking configuration structure`

### 5.2: Implement parallel booking with session management

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

**Phase**: 3.1 - Update Selenium driver management (COMPLETE)  
**Last Commit**: Ready to commit Phase 3.1  
**Next Step**: Commit Phase 3.1, then start Phase 3.2 (smart browser detection)
