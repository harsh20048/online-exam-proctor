Write-Host "Setting up database for Online Exam Proctor"
Write-Host ""
Write-Host "Please enter your MySQL root password when prompted"
Write-Host ""

# PowerShell way to pipe content to a command
Get-Content setup_database.sql | mysql -u root -p

Write-Host ""
Write-Host "Database setup complete!"
pause 