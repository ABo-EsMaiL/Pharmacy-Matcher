@echo off
chcp 65001 >nul
title Pharmacy Matcher - Setup

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║          Pharmacy Matcher - Setup Installer          ║
echo ║          نظام مطابقة الأدوية - التثبيت               ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo       Done.
) else (
    echo       Already exists.
)

echo.
echo [2/4] Installing project requirements...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet pywebview
echo       Done.

echo.
echo [3/4] Installing MSEMAX requirements (if present)...
if exist "MSEMAX\requirements.txt" (
    pip install --quiet -r MSEMAX\requirements.txt
    echo       Done.
) else (
    echo       MSEMAX folder not found, skipping.
)

echo.
echo [4/4] Creating Desktop shortcut...
:: Create a VBS script to make a shortcut
set SCRIPT_PATH=%~dp0run.bat
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Pharmacy Matcher.lnk
set ICON_PATH=%~dp0desktop_app\static\icon.ico

:: Write VBS to create shortcut
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo Set Shortcut = WshShell.CreateShortcut("%SHORTCUT_PATH%") >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.TargetPath = "%SCRIPT_PATH%" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.WindowStyle = 7 >> "%TEMP%\create_shortcut.vbs"
echo Shortcut.Description = "Pharmacy Matcher - نظام مطابقة الأدوية" >> "%TEMP%\create_shortcut.vbs"
if exist "%ICON_PATH%" (
    echo Shortcut.IconLocation = "%ICON_PATH%" >> "%TEMP%\create_shortcut.vbs"
)
echo Shortcut.Save >> "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"
echo       Shortcut created on Desktop.

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║              Setup completed successfully!           ║
echo ║         Double-click "Pharmacy Matcher" on Desktop   ║
echo ╚══════════════════════════════════════════════════════╝
echo.
pause
