# PowerShell script to set up MySQL database for Online Exam Proctor

Write-Host "Setting up MySQL database for Online Exam Proctor..." -ForegroundColor Green

$sqlCommands = @"
CREATE DATABASE IF NOT EXISTS examproctordb;
USE examproctordb;
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Password VARCHAR(100) NOT NULL,
    Role VARCHAR(20) NOT NULL
);
INSERT INTO students (Name, Email, Password, Role) VALUES ('Admin', 'admin@example.com', 'admin123', 'ADMIN');
INSERT INTO students (Name, Email, Password, Role) VALUES ('Student1', 'student1@example.com', 'student123', 'STUDENT');
"@

# Save to a temporary file
$tempFile = "temp_commands.sql"
$sqlCommands | Out-File -FilePath $tempFile -Encoding ASCII

Write-Host "Running MySQL commands..." -ForegroundColor Yellow
Write-Host "Please enter your MySQL password when prompted."

# Try with an empty password first
try {
    # Use cmd.exe to execute the command properly
    Write-Host "Trying with empty password..." -ForegroundColor Yellow
    cmd.exe /c "mysql -u root < $tempFile"
    Write-Host "Successfully connected with no password!" -ForegroundColor Green
} catch {
    # If that fails, try with a password prompt
    Write-Host "Failed to connect without password, trying with password prompt..." -ForegroundColor Yellow
    cmd.exe /c "mysql -u root -p < $tempFile"
}

# Clean up
Remove-Item $tempFile

Write-Host "`nDatabase setup complete!" -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 