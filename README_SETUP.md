# Online Exam Proctor - Setup Instructions

This project is an Online Exam Proctoring system using computer vision and artificial intelligence to detect cheating behaviors during online exams.

## System Requirements

- Windows, macOS, or Linux
- Python 3.7 or later
- Webcam
- MySQL Server (e.g., XAMPP, MySQL Workbench)
- 4GB+ RAM recommended (for ML processing)

## Required Dependencies

```
pip install flask flask-mysqldb keyboard opencv-python mediapipe pyautogui pygetwindow ultralytics pyaudio dlib
```

### Installing face_recognition 

The system uses face_recognition which depends on dlib. This can be challenging to install on Windows. Here are instructions:

#### Option 1: Using pre-built wheels

```
pip install cmake
pip install dlib
pip install face-recognition
```

#### Option 2: Using conda (recommended)

```
conda create -n exam-proctor python=3.8
conda activate exam-proctor
conda install -c conda-forge dlib
pip install face-recognition
pip install flask flask-mysqldb keyboard opencv-python mediapipe pyautogui pygetwindow ultralytics pyaudio
```

## Database Setup

1. Start your MySQL server (XAMPP, MySQL Workbench, or command line)
2. Make sure your MySQL root user has password set to 'root' (or modify app.py to match your MySQL password)
3. Create the database and tables by running the setup_database.sql script:
   ```
   mysql -u root -p < setup_database.sql
   ```
   Or you can run the setup_database.bat file on Windows.
   
   Alternatively, you can open the script in MySQL Workbench and execute it.

## Directory Structure Setup

Make sure these directories exist for storing outputs:

```
mkdir -p static/OutputVideos
mkdir -p static/Profiles
mkdir -p static/OuputAudios
```

## Running the Application

```
python app.py
```

Access the application at: http://127.0.0.1:5000/

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
- Head movement detection
- Multiple person detection
- Screen monitoring
- Electronic device detection
- Admin dashboard for results and student management

## Common Issues and Solutions

1. **face_recognition/dlib installation issues**: Try the conda installation method if pip fails.
2. **MySQL connection issues**: Ensure MySQL server is running and credentials in app.py match your setup.
3. **Camera access**: Ensure your browser allows camera access.
4. **Missing directories**: Create the output directories manually if missing.

## Note

This application requires significant permissions to function properly, including:
- Camera access
- Screen recording
- Keyboard monitoring

These permissions are necessary for the proctoring features to work correctly. 