@echo off
echo Starting Ready Set Realtor Server...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run database migrations
alembic upgrade head

REM Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM Deactivate virtual environment
if exist venv\Scripts\deactivate.bat (
    call venv\Scripts\deactivate.bat
)

pause
