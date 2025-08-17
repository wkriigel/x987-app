Param([string]$Py = "python")
$ErrorActionPreference = "Stop"

# Paths – compute relative to this script's location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppRoot = Split-Path -Parent $ScriptDir
$Venv = Join-Path $AppRoot ".venv"
$Reqs = Join-Path $AppRoot "requirements.txt"

Write-Host "==> Creating venv at $Venv"
& $Py -m venv $Venv

Write-Host "==> Activating venv"
. (Join-Path $Venv "Scripts\Activate.ps1")

Write-Host "==> Upgrading pip"
& python -m pip install --upgrade pip

Write-Host "==> Installing requirements from $Reqs"
& python -m pip install -r $Reqs

Write-Host "==> Installing Playwright (Chromium)"
& python -m playwright install chromium

Write-Host "✅ Setup complete. To run:"
Write-Host "   . $Venv\Scripts\Activate.ps1"
Write-Host "   python -m x987"
