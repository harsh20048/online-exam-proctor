# Online Exam Proctor

A comprehensive online exam proctoring system that uses computer vision and AI to detect cheating behaviors.

## Features

- Face recognition for identity verification
- Head movement detection
- Multiple person detection
- Screen monitoring
- Electronic device detection
- Voice detection
- Admin dashboard to view results and violations

## Quick Start

1. **Set up the database**:
   - Make sure MySQL server is running
   - Run `setup_db.ps1` to set up the database (PowerShell)
   - If prompted, enter your MySQL root password

2. **Run the application**:
   - Run `run_app.bat` to start the application
   - Open your browser and go to: http://127.0.0.1:5000/

3. **Login Credentials**:
   - Admin: 
     - Email: admin@example.com
     - Password: admin123
   - Student:
     - Email: student1@example.com
     - Password: student123

## Troubleshooting

### MySQL Connection Issues
If you get a MySQL connection error:

1. Check if your MySQL server is running
2. Verify the database exists: `examproctordb`
3. Make sure your MySQL username and password match the settings in `app.py`
4. If your MySQL setup is different, edit the MySQL configuration in `app.py`:

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Set to your MySQL password
app.config['MYSQL_DB'] = 'examproctordb'
```

### Permission Issues
The application requires:
- Camera access
- Screen recording access
- Keyboard monitoring

Make sure to allow these permissions when prompted.

## System Requirements

- Windows 10 or later
- Python 3.7+
- MySQL Server
- Webcam 