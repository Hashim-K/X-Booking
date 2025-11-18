# X Booking Automation

An automated booking system for TU Delft X fitness slots with both a web-based React interface and a native Python GUI.

## Features

- Two user interface options:
  - Modern React web application
  - Native Python Tkinter GUI
- Calendar for date selection
- Customizable time slot selection with priority ordering
- Automatic retry mechanism with adjustable interval
- Visual feedback on booking status
- Secure credential management through environment variables

## Prerequisites

- Python 3.9 or higher
- Chrome browser installed
- TU Delft account credentials
- Node.js and npm (for the React web app)
- Poetry (for managing Python dependencies)

## Setup Guide

### 1. Poetry Environment Setup

**Important:** Install and configure Poetry before running the project.

```bash
# Verify installation
poetry --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/omar-elamin/X-Script.git
cd X-Script
```

### 3. Install Python Dependencies (with Poetry)

Poetry will automatically create a virtual environment for this project.

```bash
poetry install
```

If you want to enter the virtual environment manually:

```bash
poetry env activate
```

This will print a command (a path to an `activate` script). Then just run the printed command.

### 4. Install Node.js Dependencies (for the React web app)

```bash
npm install
```

### 5. Create a `.env` File

Inside the project folder:

```
TU_USERNAME=your_username
TU_PASSWORD=your_password
```

## Usage

### Option 1: Python Tkinter GUI

```bash
# Run the Python application
poetry run python main.py
```

### Option 2: React Web Application

```bash
# Start the application (either method works)
npm start -- -p 8008
# OR
./run.bat  # Windows only
```

Open your browser and navigate to `http://localhost:8008`

### Run Script (Windows)

The `run.bat` script automates the process of starting the React web application:

- Checks for Node.js and npm installations
- Installs npm dependencies if needed
- Starts the Next.js application on port 8008

```bash
.\run.bat
```

## Working with the Application

### Using the GUI Interface

1. Select a date using the calendar
2. Check the time slots you want to book
3. Arrange the priority order using the ↑↓ arrows
4. Set your preferred retry interval (default: 300 seconds)
5. Click "Book Selected Slots" to start the booking process
6. Use "Stop Retrying" to cancel the automatic retry process

### Using the Web Interface

1. Select a date using the calendar
2. Check the time slots you want to book
3. Drag and drop to arrange priority order
4. Set your preferred retry interval
5. Click "Book Selected Slots" to start the booking process
6. Use "Stop Retrying" to cancel the automatic retry process

## How It Works

- The booking system tries slots in the order you prioritized them
- If a slot is unavailable, it automatically tries the next preferred time
- The retry interval can be adjusted through either UI
- The React app communicates with the Python script via API endpoints
- The browser automation runs headless (invisible) to reduce resource usage

## Troubleshooting

If you encounter issues:
1. Ensure Chrome browser is installed and up to date
2. Verify your internet connection
3. Check that your TU Delft credentials are correct in the `.env` file
4. Make sure all dependencies are properly installed
5. Verify your conda environment is activated properly

## Security

- Credentials are stored locally in the `.env` file
- The `.env` file is excluded from version control
- Never share your credentials or the `.env` file

## Dependencies

### Python
- python-dotenv: Environment variable management
- selenium: Web automation
- webdriver-manager: Chrome driver management
- numpy: Numerical operations
- tkcalendar: Calendar widget for GUI

### JavaScript (React App)
- Next.js: React framework
- React: UI library
- React Calendar: Date picker component
- React Beautiful DnD: Drag and drop functionality
- Tailwind CSS: Styling
