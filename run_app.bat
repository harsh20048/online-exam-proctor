@echo off
echo ===================================================
echo       STARTING ONLINE EXAM PROCTOR SYSTEM
echo ===================================================
echo.

if exist The-Online-Exam-Proctor-main\app.py (
    cd The-Online-Exam-Proctor-main
)

echo Starting application...
python app.py

echo.
echo Application stopped.
pause 