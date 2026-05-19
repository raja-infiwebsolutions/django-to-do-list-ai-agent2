@echo off
REM Django Todo App Setup Script for Windows
REM This script installs dependencies, runs migrations, and prepares the project

echo.
echo ============================================================
echo Django Todo App Setup
echo ============================================================
echo.

REM Get Python executable
for /f "delims=" %%i in ('where python') do set PYTHON=%%i

if "%PYTHON%"=="" (
    echo Error: Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

echo Using Python: %PYTHON%
echo.

REM Step 1: Install dependencies
echo ============================================================
echo Installing Python dependencies...
echo ============================================================
%PYTHON% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Step 2: Check Django configuration
echo ============================================================
echo Checking Django configuration...
echo ============================================================
%PYTHON% manage.py check
if %errorlevel% neq 0 (
    echo Error: Django configuration check failed
    pause
    exit /b 1
)
echo.

REM Step 3: Run migrations
echo ============================================================
echo Running database migrations...
echo ============================================================
%PYTHON% manage.py migrate
if %errorlevel% neq 0 (
    echo Error: Migration failed
    pause
    exit /b 1
)
echo.

REM Step 4: Collect static files
echo ============================================================
echo Collecting static files...
echo ============================================================
%PYTHON% manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo Warning: Static file collection failed (may not be critical for dev)
)
echo.

echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Access the application at:
echo   http://localhost:8000
echo   Admin: http://localhost:8000/admin
echo.
echo ============================================================
pause
