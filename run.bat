@echo off
setlocal

echo ==========================================================
echo X-Booking Development Environment Setup
echo ==========================================================
echo.

echo Checking Poetry installation...
where poetry >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Poetry not found. Please install Poetry:
    echo https://python-poetry.org/docs/#installation
    exit /b 1
)
echo   [OK] Poetry found

echo Checking Node.js installation...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js not found. Please install Node.js:
    echo https://nodejs.org/
    exit /b 1
)
echo   [OK] Node.js found

echo Checking npm installation...
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm not found. Please install npm.
    exit /b 1
)
echo   [OK] npm found

echo.
echo Installing Python dependencies with Poetry...
call poetry install
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install Python dependencies
    exit /b 1
)

echo.
echo Installing Node.js dependencies with npm...
if exist package.json (
    if not exist node_modules (
        call npm install
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install npm dependencies
            exit /b 1
        )
    )
)

echo.
echo Starting development server on port 8008...
echo Press Ctrl+C to stop
echo.

call npm run dev

exit /b 0
