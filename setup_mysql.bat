@echo off
echo Setting up database for Online Exam Proctor...

REM Create a temporary SQL file with commands
echo CREATE DATABASE IF NOT EXISTS examproctordb; > temp_commands.sql
echo USE examproctordb; >> temp_commands.sql
echo DROP TABLE IF EXISTS students; >> temp_commands.sql
echo CREATE TABLE students ( >> temp_commands.sql
echo     ID INT AUTO_INCREMENT PRIMARY KEY, >> temp_commands.sql
echo     Name VARCHAR(100) NOT NULL, >> temp_commands.sql
echo     Email VARCHAR(100) NOT NULL, >> temp_commands.sql
echo     Password VARCHAR(100) NOT NULL, >> temp_commands.sql
echo     Role VARCHAR(20) NOT NULL >> temp_commands.sql
echo ); >> temp_commands.sql
echo INSERT INTO students (Name, Email, Password, Role) VALUES ('Admin', 'admin@example.com', 'admin123', 'ADMIN'); >> temp_commands.sql
echo INSERT INTO students (Name, Email, Password, Role) VALUES ('Student1', 'student1@example.com', 'student123', 'STUDENT'); >> temp_commands.sql

REM Run the commands
echo Running MySQL commands...
echo Please enter your MySQL password when prompted:
mysql -u root -p < temp_commands.sql

REM Clean up
del temp_commands.sql

echo Database setup complete!
pause 