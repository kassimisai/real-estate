@echo off
echo Running Ready Set Realtor Tests...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install test dependencies
pip install pytest pytest-asyncio httpx

REM Run the tests
pytest tests/ -v

REM Deactivate virtual environment
if exist venv\Scripts\deactivate.bat (
    call venv\Scripts\deactivate.bat
)

pause
