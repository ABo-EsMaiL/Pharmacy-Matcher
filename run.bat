@echo off
cd /d "%~dp0"

:: Check Conda environment first (recommended)
if exist "D:\miniconda3\envs\venv\pythonw.exe" (
    start "" /B "D:\miniconda3\envs\venv\pythonw.exe" desktop_app\app.py
    exit /b 0
)

:: Try to use local venv if it exists
if exist "venv\Scripts\pythonw.exe" (
    start "" /B venv\Scripts\pythonw.exe desktop_app\app.py
    exit /b 0
)

if exist ".venv\Scripts\pythonw.exe" (
    start "" /B .venv\Scripts\pythonw.exe desktop_app\app.py
    exit /b 0
)

:: Fallback to global pythonw (no terminal)
start "" /B pythonw desktop_app\app.py 2>nul

:: If pythonw fails, fallback to standard python
if %ERRORLEVEL% NEQ 0 (
    start "" /B python desktop_app\app.py
)
