@echo off
title Pharmacy Matcher - Developer (Conda)
cd /d "%~dp0"

echo Running in Developer Mode (Conda)...
if exist "D:\miniconda3\envs\venv\python.exe" (
    "D:\miniconda3\envs\venv\python.exe" desktop_app\app.py
) else (
    python desktop_app\app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application closed with an error.
    pause
)