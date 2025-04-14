@echo off
echo Setting up database for Online Exam Proctor
echo.
echo Please enter your MySQL root password when prompted
echo.
cmd /c "mysql -u root -p < setup_database.sql"
echo.
echo Database setup complete!
pause 