import cv2
import numpy as np
import time

class FaceDetector:
    def __init__(self):
        self.cap = None
        # Load Haar cascade classifiers
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        
        if self.face_cascade.empty():
            raise ValueError("Error: Could not load face cascade classifier")
        if self.eye_cascade.empty():
            raise ValueError("Error: Could not load eye cascade classifier")
        
    def initialize_camera(self):
        try:
            # Release existing camera if any
            if self.cap is not None:
                self.cap.release()
                self.cap = None
                time.sleep(1)  # Give time for camera to be released
                
            # Try multiple camera initialization methods
            camera_indices = [0, 1, 2, 3]  # Try multiple camera indices
            for index in camera_indices:
                try:
                    self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                    if self.cap.isOpened():
                        break
                        
                    self.cap = cv2.VideoCapture(index)  # Try without DSHOW
                    if self.cap.isOpened():
                        break
                except:
                    continue
                    
            if not self.cap or not self.cap.isOpened():
                print("Failed to initialize camera with any method")
                return False
                
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Warm up the camera
            for _ in range(15):  # Increased warmup frames
                success, _ = self.cap.read()
                if not success:
                    print("Warmup frame failed")
                time.sleep(0.1)
                
            # Verify camera is working
            success, frame = self.cap.read()
            if not success or frame is None:
                print("Camera is not working properly")
                self.cap.release()
                self.cap = None
                return False
                
            return True
            
        except Exception as e:
            print(f"Error in initialize_camera: {str(e)}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            return False
        
    def get_frame(self):
        try:
            if self.cap is None or not self.cap.isOpened():
                if not self.initialize_camera():
                    return None, "Camera not available"
                    
            success, frame = self.cap.read()
            if not success or frame is None:
                print("Failed to read frame from camera")
                self.cap.release()
                self.cap = None
                return None, "Failed to read frame"
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Draw rectangles around detected faces and detect eyes
            face_detected = False
            for (x, y, w, h) in faces:
                face_detected = True
                # Draw face rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Region of interest for eyes
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                # Detect eyes
                eyes = self.eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(20, 20)
                )
                
                # Draw rectangles around eyes
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Add status text
            if not face_detected:
                cv2.putText(frame, "No face detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                status = "No face detected"
            elif len(faces) > 1:
                cv2.putText(frame, "Multiple faces detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                status = "Multiple faces detected"
            else:
                cv2.putText(frame, "Face detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                status = "Face detected"
            
            return frame, status
            
        except Exception as e:
            print(f"Error in get_frame: {str(e)}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            return None, f"Error: {str(e)}"
            
    def release(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except:
                pass
            finally:
                self.cap = None 