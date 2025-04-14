CREATE DATABASE IF NOT EXISTS examproctordb;

USE examproctordb;

-- Create the students table
CREATE TABLE IF NOT EXISTS students (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Password VARCHAR(100) NOT NULL,
    Role VARCHAR(20) NOT NULL
);

-- Insert an admin user
INSERT INTO
    students (Name, Email, Password, Role)
VALUES
    (
        'Admin',
        'admin@example.com',
        'admin123',
        'ADMIN'
    );

-- Insert some sample student users
INSERT INTO
    students (Name, Email, Password, Role)
VALUES
    (
        'Student1',
        'student1@example.com',
        'student123',
        'STUDENT'
    );