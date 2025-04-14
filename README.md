# Online Exam Proctor

An intelligent online examination proctoring system that uses computer vision and AI to monitor exam sessions in real-time.

## Features

- Real-time face detection and tracking
- Multiple face detection to prevent impersonation
- Head movement detection
- Prohibited object detection (phones, books, etc.)
- Violation recording and reporting
- Web-based interface for easy access
- Database integration for storing exam results and violations

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- Flask
- MySQL
- MediaPipe
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/online-exam-proctor.git
cd online-exam-proctor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# For Windows
setup_db.ps1

# For Linux/Mac
./setup_db.sh
```

4. Download required models:
```bash
python download_models.py
```

## Usage

1. Start the application:
```bash
# For Windows
run_app.bat

# For Linux/Mac
python app.py
```

2. Access the web interface at `http://localhost:5000`

3. Login with your credentials:
   - Admin: admin@example.com / admin123
   - Student: student1@example.com / student123

## Project Structure

- `app.py` - Main Flask application
- `camera_alldetectors.py` - Face and object detection implementation
- `utils.py` - Utility functions
- `models/` - AI model files
- `static/` - Static web assets
- `setup_db.ps1` - Database setup script
- `requirements.txt` - Python dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for computer vision capabilities
- MediaPipe for face mesh detection
- YOLO for object detection
- Flask for web framework 