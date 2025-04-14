# Online Exam Proctor - Setup and Run Instructions

## Prerequisites
1. Python (3.7 or later)
2. MySQL server
3. Webcam

## Step 1: Install Required Packages
```
pip install flask flask-mysqldb keyboard opencv-python
```

## Step 2: Set Up Database
1. Start your MySQL server (XAMPP, MySQL Workbench, or command line)
2. Create the database and tables by running the SQL script:
   ```
   mysql -u root -p < setup_database.sql
   ```
   Or open the script in MySQL Workbench and execute it.

## Step 3: Run the Application
```
python app.py
```

## Step 4: Access the Application
Open your browser and go to: http://127.0.0.1:5000/

## Login Credentials
- Admin: 
  - Email: admin@example.com
  - Password: admin123
- Student:
  - Email: student1@example.com
  - Password: student123

## Features
- Student authentication
- Face recognition for exam proctoring
- System compatibility check
- Admin dashboard for results and student management
- Cheating detection during exam

## Notes
- The application requires camera access, so make sure to allow it when prompted by your browser.
- The database connection is configured for a local MySQL server with no password. If your setup is different, modify the MySQL configuration in app.py. 