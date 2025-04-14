# PowerShell Script to set up Online Exam Proctor System

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "       SETTING UP ONLINE EXAM PROCTOR SYSTEM        " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host

Write-Host "Step 1: Setting up directories..." -ForegroundColor Green
& "$PSScriptRoot\setup_directories.ps1"

Write-Host "Step 2: Installing required Python packages..." -ForegroundColor Green
if (Test-Path "$PSScriptRoot\requirements.txt") {
    pip install -r "$PSScriptRoot\requirements.txt"
} else {
    Write-Host "Warning: requirements.txt not found!" -ForegroundColor Yellow
}

Write-Host "Step 3: Checking MongoDB connection..." -ForegroundColor Green
Write-Host "Make sure MongoDB service is running." -ForegroundColor Yellow
Write-Host "The application will automatically create required collections on first run."

Write-Host
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "       SETUP COMPLETED SUCCESSFULLY                 " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host
Write-Host "You can now run the application using run_app.bat"
Write-Host 