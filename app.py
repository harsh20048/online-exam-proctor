from face_detection import FaceDetector
import cv2
import numpy as np
import time
import keyboard
from flask import Flask, render_template, request, redirect, url_for, flash, Response
import utils

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/exam')
def exam():
    try:
        # Check if studentInfo exists
        if studentInfo is None:
            flash("Please login first before taking the exam", category="error")
            return redirect(url_for('main'))
            
        # Initialize face detector
        face_detector = FaceDetector()
        if not face_detector.initialize_camera():
            flash("Error: Could not open camera. Please check your camera connection.", category="error")
            return redirect(url_for('systemCheck'))
            
        # Hook keyboard shortcuts
        keyboard.hook(utils.shortcut_handler)
        return render_template('Exam.html')
    except Exception as e:
        flash(f"Error initializing exam: {str(e)}", category="error")
        return redirect(url_for('systemCheck'))

def capture_by_frames():
    face_detector = FaceDetector()
    retry_count = 0
    max_retries = 3
    
    try:
        if not face_detector.initialize_camera():
            # Create an error image
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_img, "Camera Error", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(error_img, "Check camera connection", (100, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(error_img, "Try refreshing page", (120, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', error_img)
            error_frame = buffer.tobytes()
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
            return
            
        while True:
            frame, status = face_detector.get_frame()
            
            if frame is None:
                retry_count += 1
                print(f"Error: {status} (Retry {retry_count}/{max_retries})")
                
                if retry_count >= max_retries:
                    # Create an error image
                    error_img = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(error_img, "Camera Error", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(error_img, "Please refresh the page", (100, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', error_img)
                    error_frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                    break
                    
                time.sleep(0.5)  # Wait before retrying
                continue
                
            retry_count = 0  # Reset retry count on successful frame
                
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    except Exception as e:
        print(f"Error in capture_by_frames: {str(e)}")
        # Create an error frame
        error_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_img, f"Camera Error: {str(e)}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', error_img)
        error_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
    finally:
        face_detector.release() 