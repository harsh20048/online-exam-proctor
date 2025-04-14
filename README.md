# Online Exam Proctor

A comprehensive online examination system with AI-powered proctoring capabilities.

## Features

- **AI-Powered Proctoring**
  - Face detection and recognition
  - Head movement tracking
  - Multiple person detection
  - Real-time monitoring

- **Exam Management**
  - Create and manage exams
  - Set time limits
  - Randomize questions
  - Automatic grading

- **User Management**
  - Student registration
  - Admin dashboard
  - Role-based access control

## Installation

1. Clone the repository:
```bash
git clone https://github.com/harsh20048/online-exam-proctor.git
cd online-exam-proctor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# On Windows
.\setup_db.ps1

# On Linux/Mac
./setup_db.sh
```

5. Run the application:
```bash
python app.py
```

## Configuration

1. Create a `.env` file in the root directory:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=mysql://username:password@localhost/examproctordb
```

2. Update the database configuration in `config.py` if needed.

## Usage

1. Access the application at `http://localhost:5000`
2. Login credentials:
   - Admin: admin@example.com / admin123
   - Student: student1@example.com / student123

## Project Structure

```
online-exam-proctor/
├── app.py              # Main application file
├── camera_alldetectors.py  # Face detection and tracking
├── config.py           # Configuration settings
├── models/             # ML models
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
├── utils.py            # Utility functions
└── requirements.txt    # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV for computer vision capabilities
- MediaPipe for face detection
- Flask for web framework
- MySQL for database management 