@echo off
setlocal enabledelayedexpansion

REM Paths relative to this script
set "SCRIPT_DIR=%~dp0"
set "APP_ROOT=%SCRIPT_DIR%\.."
set "VENV=%APP_ROOT%\.venv"
set "REQS=%APP_ROOT%\requirements.txt"

echo ==> Creating venv at %VENV%
python -m venv "%VENV%"

echo ==> Activating venv
call "%VENV%\Scripts\activate.bat"

echo ==> Upgrading pip
python -m pip install --upgrade pip

echo ==> Installing requirements from %REQS%
python -m pip install -r "%REQS%"

echo ==> Installing Playwright (Chromium)
python -m playwright install chromium

echo ✅ Setup complete. To run:
echo    call "%VENV%\Scripts\activate.bat"
echo    python -m x987
