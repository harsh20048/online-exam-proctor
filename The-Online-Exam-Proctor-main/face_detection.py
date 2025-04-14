import cv2
import numpy as np
import time

# Global camera manager
class CameraManager:
    _instance = None
    
    @staticmethod
    def get_instance():
        if CameraManager._instance is None:
            CameraManager._instance = CameraManager()
        return CameraManager._instance
    
    def __init__(self):
        self.cap = None
        self.in_use = False
        self.last_access = 0
    
    def get_camera(self):
        self.in_use = True
        self.last_access = time.time()
        
        if self.cap is None or not self.cap.isOpened():
            self.initialize_camera()
        
        return self.cap
    
    def release_camera(self):
        self.in_use = False
    
    def initialize_camera(self):
        # Release existing camera if any
        if self.cap is not None:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
            
        # Try multiple camera initialization methods
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)  # Try without DSHOW
            
        if not self.cap.isOpened():
            # Try with different camera indices
            for i in range(1, 4):  # Try up to 3 different camera indices
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    break
                    
        if not self.cap.isOpened():
            print("Failed to initialize camera")
            return False
            
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
        
        # Warm up the camera
        for _ in range(10):  # Increased warmup frames
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
            
        print("Camera initialized successfully")
        return True
        
    def force_release(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        self.in_use = False

class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')
        self.camera_manager = CameraManager.get_instance()
        
    def initialize_camera(self):
        return self.camera_manager.initialize_camera()
        
    def get_frame(self):
        cap = self.camera_manager.get_camera()
        if cap is None or not cap.isOpened():
            if not self.camera_manager.initialize_camera():
                return None, "Camera not available"
            cap = self.camera_manager.get_camera()
            if cap is None or not cap.isOpened():
                return None, "Camera initialization failed"
                
        try:
            success, frame = cap.read()
            if not success or frame is None:
                print("Failed to read frame from camera")
                self.camera_manager.force_release()
                return None, "Failed to read frame"
                
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Region of interest for eyes (within face)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                # Detect eyes within the face region
                eyes = self.eye_cascade.detectMultiScale(roi_gray)
                
                # Draw rectangles around detected eyes
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Add text to guide the user
            if len(faces) == 0:
                cv2.putText(frame, "No face detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                status = "No face detected"
            elif len(faces) > 1:
                cv2.putText(frame, "Multiple faces detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                status = "Multiple faces detected"
            else:
                cv2.putText(frame, "Face detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                status = "Face detected"
                
            return frame, status
                
        except Exception as e:
            print(f"Error in get_frame: {str(e)}")
            self.camera_manager.force_release()
            return None, f"Error: {str(e)}"
            
    def release(self):
        self.camera_manager.release_camera()
        
    def get_camera(self):
        return self.camera_manager.get_camera() 