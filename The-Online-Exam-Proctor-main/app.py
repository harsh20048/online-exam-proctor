import math
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, session,redirect,url_for,Response,flash
import os
from pymongo import MongoClient
import json
import io
import numpy as np
from enum import Enum
import warnings
import threading
import utils
import random
import time
import cv2
import keyboard

#variables
studentInfo=None
camera=None
profileName=None

#Flak's Application Confguration
warnings.filterwarnings("ignore")
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'xyz'
# app.config["MONGO_URI"] = "mongodb://localhost:27017/"
os.path.dirname("../templates")

#Flak's Database Configuration - MongoDB
try:
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["examproctordb"]
    students_collection = db["students"]
    
    # Check if admin user exists, if not create it
    if students_collection.count_documents({"Email": "admin@example.com"}) == 0:
        students_collection.insert_one({
            "Id": 1,
            "Name": "Admin User",
            "Email": "admin@example.com",
            "Password": "admin123",
            "Role": "ADMIN"
        })
    
    # Check if sample student exists, if not create it
    if students_collection.count_documents({"Email": "student1@example.com"}) == 0:
        students_collection.insert_one({
            "Id": 2,
            "Name": "Student One",
            "Email": "student1@example.com",
            "Password": "student123",
            "Role": "STUDENT"
        })
        
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection error: {e}")

executor = ThreadPoolExecutor(max_workers=4)  # Adjust the number of workers as needed

# Dictionary to store background tasks
background_tasks = {}

#Function to show face detection's Rectangle in Face Input Page
def capture_by_frames():
    global camera
    
    try:
        # First verify camera is initialized and opened
        if not hasattr(utils, 'cap') or utils.cap is None or not utils.cap.isOpened():
            print("Camera not properly initialized in capture_by_frames, attempting to fix")
            
            # Try to release any existing camera
            if hasattr(utils, 'cap') and utils.cap is not None:
                try:
                    utils.cap.release()
                except:
                    pass
                    
            # Initialize a new camera
            utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not utils.cap.isOpened():
                utils.cap = cv2.VideoCapture(0)  # Try alternate initialization
                
            if not utils.cap.isOpened():
                print("Failed to initialize camera in capture_by_frames")
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
                
        print("Camera verified in capture_by_frames")
                
        # Read a few frames to warm up the camera
        for i in range(3):
            try:
                success, _ = utils.cap.read()
                if not success:
                    print(f"Warmup frame {i} failed in capture_by_frames")
                time.sleep(0.1)
            except Exception as e:
                print(f"Error during camera warmup: {e}")
                
        # Main camera loop
        frame_count = 0
        while True:
            frame_count += 1
            try:
                success, frame = utils.cap.read()
                if not success:
                    print(f"Failed to read frame {frame_count} from camera")
                    if frame_count > 5:  # Only show error after multiple failures
                        error_img = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(error_img, "Camera Error", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(error_img, "Please refresh the page", (100, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        ret, buffer = cv2.imencode('.jpg', error_img)
                        frame = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    continue
                else:
                    # Draw a guide rectangle to help position the face
                    h, w, _ = frame.shape
                    center_x, center_y = w//2, h//2
                    rect_width, rect_height = 300, 350
                    top_left = (center_x - rect_width//2, center_y - rect_height//2)
                    bottom_right = (center_x + rect_width//2, center_y + rect_height//2)
                    
                    # Draw a green rectangle as a guide
                    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 3)
                    cv2.putText(frame, "Position your face inside", (center_x - 150, center_y - rect_height//2 - 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Find faces
                    detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
                    if detector.empty():
                        print("Error: Haar cascade classifier is empty")
                        cv2.putText(frame, "Error: Face detection not available", (50, 50), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = detector.detectMultiScale(gray_frame, 1.1, 5, minSize=(100, 100))
                        
                        # Draw the rectangle around each face
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        
                        # Add text to guide the user
                        if len(faces) == 0:
                            cv2.putText(frame, "No face detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        elif len(faces) > 1:
                            cv2.putText(frame, "Multiple faces detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        else:
                            # Check if face is within the guide rectangle
                            face_x, face_y, face_w, face_h = faces[0]
                            face_center_x = face_x + face_w//2
                            face_center_y = face_y + face_h//2
                            
                            if (top_left[0] < face_center_x < bottom_right[0] and 
                                top_left[1] < face_center_y < bottom_right[1]):
                                cv2.putText(frame, "Face detected - Good position", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            else:
                                cv2.putText(frame, "Center your face in the green box", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error in capture_by_frames: {e}")
                # Create an error frame if an exception occurs
                error_img = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_img, f"Camera Error: {str(e)}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                ret, buffer = cv2.imencode('.jpg', error_img)
                error_frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
    except Exception as e:
        print(f"Severe error in capture_by_frames: {e}")
        # Create an error frame if an exception occurs
        error_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_img, f"Camera Error: {str(e)}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', error_img)
        error_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')

#Function to run Cheat Detection when we start run the Application
@app.before_request
def start_loop():
    # Skip starting background tasks for camera-intensive routes
    if request.endpoint in ['video_capture', 'saveFaceInput', 'confirmFaceInput']:
        return
        
    try:
        global background_tasks
        
        # Initialize utils when needed
        if not hasattr(utils, 'fr'):
            print("Initializing FaceRecognition")
            utils.fr = utils.FaceRecognition()
            
        if not hasattr(utils, 'a'):
            print("Initializing Audio Recorder")
            utils.a = utils.Recorder()
            
        # Only start background tasks for exam route
        if request.endpoint == 'exam' and not background_tasks:
            print("Starting background detection tasks")
            # Start the background tasks for cheat detection
            background_tasks['cheat1'] = executor.submit(utils.cheat_Detection1)
            background_tasks['cheat2'] = executor.submit(utils.cheat_Detection2)
            background_tasks['face'] = executor.submit(utils.fr.run_recognition)
            background_tasks['audio'] = executor.submit(utils.a.record)
            
    except Exception as e:
        print(f"Error in start_loop: {e}")  # Log error but don't interrupt the request

#Login Related
@app.route('/')
def main():
    try:
        # Test the database connection
        _ = db.list_collection_names()
    except Exception as e:
        error_message = str(e)
        return f"""
        <h1>Database Connection Error</h1>
        <p>Could not connect to the MongoDB database. Please check your MongoDB setup:</p>
        <p>Error: {error_message}</p>
        <p>Make sure:</p>
        <ul>
            <li>MongoDB server is running on localhost:27017</li>
            <li>MongoDB service is started</li>
        </ul>
        """
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global studentInfo
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user in MongoDB
        user = students_collection.find_one({"Email": username, "Password": password})
        
        if user is None:
            flash('Your Email or Password is incorrect, try again.', category='error')
            return redirect(url_for('main'))
        else:
            studentInfo = {
                "Id": user["Id"],
                "Name": user["Name"],
                "Email": user["Email"],
                "Password": user["Password"]
            }
            
            if user["Role"] == 'STUDENT':
                utils.Student_Name = user["Name"]
                return redirect(url_for('rules'))
            else:
                return redirect(url_for('adminStudents'))

@app.route('/logout')
def logout():
    global studentInfo, profileName
    # Clear user data
    studentInfo = None
    profileName = None
    
    # Release camera if it's open
    if hasattr(utils, 'cap') and utils.cap is not None and utils.cap.isOpened():
        utils.cap.release()
        utils.cap = None
        
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('main'))

#Student Related
@app.route('/rules')
def rules():
    return render_template('ExamRules.html')

@app.route('/faceInput')
def faceInput():
    # Check if studentInfo exists
    if studentInfo is None:
        flash("Please login first before taking the exam", category="error")
        return redirect(url_for('main'))
    return render_template('ExamFaceInput.html')

@app.route('/video_capture')
def video_capture():
    global camera
    
    # First clean up any existing resources
    cleanup_resources()
    
    # Make sure we're starting fresh
    try:
        if hasattr(utils, 'cap') and utils.cap is not None:
            if utils.cap.isOpened():
                utils.cap.release()
            utils.cap = None
            time.sleep(0.5)  # Give time for resources to be released
            
        # Initialize new camera
        print("Initializing new camera for video capture")
        utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # Try alternate initialization if first method fails
        if not utils.cap.isOpened():
            print("First camera initialization failed, trying alternate method")
            utils.cap.release()
            utils.cap = cv2.VideoCapture(0)
            
        if not utils.cap.isOpened():
            print("All camera initialization methods failed")
            return "Error: Could not open camera. Please check your camera connection."
        
        print("Camera successfully initialized for video capture")
        return Response(capture_by_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    except Exception as e:
        print(f"Error in video_capture: {str(e)}")
        return f"Error initializing camera: {str(e)}"

@app.route('/saveFaceInput')
def saveFaceInput():
    global profileName, utils
    
    # Check if studentInfo exists
    if studentInfo is None:
        flash("Please login first before taking the exam", category="error")
        return redirect(url_for('main'))
    
    try:
        # Temporarily disable background processes
        print("Temporarily stopping background processes for face capture")
        original_flag = utils.Globalflag
        utils.Globalflag = False
        time.sleep(1)  # Give time for threads to notice the flag change
        
        # Safely release the camera if it exists and is open
        if hasattr(utils, 'cap') and utils.cap is not None and utils.cap.isOpened():
            utils.cap.release()
            time.sleep(1.0)  # Give the camera time to release
        
        # Create a new camera capture
        print("Opening camera for face capture")
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            flash("Error: Could not open camera. Please check your camera connection.", category="error")
            return redirect(url_for('faceInput'))
            
        # Give the camera time to warm up
        time.sleep(2.0)
        
        # Capture multiple frames to ensure the camera is ready
        print("Warming up camera")
        for i in range(10):
            success, _ = cam.read()
            if not success:
                print(f"Warmup frame {i} failed")
            time.sleep(0.1)
            
        # Now read the frame we'll actually use
        print("Capturing face image")
        success, frame = cam.read()
        if not success:
            flash("Error: Could not read from camera. Please check your camera connection.", category="error")
            cam.release()
            return redirect(url_for('faceInput'))
            
        # Verify if a face is found in the image
        try:
            detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
            if detector.empty():
                print("Error: Haar cascade classifier is empty or failed to load")
                flash("Error with face detection system. Please try again.", category="error")
                cam.release()
                return redirect(url_for('faceInput'))
                
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray_frame, 1.1, 5, minSize=(100, 100))
            
            if len(faces) == 0:
                print("No faces detected in captured frame")
                flash("No face detected. Please make sure your face is visible to the camera.", category="error")
                cam.release()
                return redirect(url_for('faceInput'))
            
            if len(faces) > 1:
                print("Multiple faces detected in captured frame")
                flash("Multiple faces detected. Please ensure only your face is visible.", category="error")
                cam.release()
                return redirect(url_for('faceInput'))
                
            # Draw rectangle around the detected face for verification
            face_x, face_y, face_w, face_h = faces[0]
            cv2.rectangle(frame, (face_x, face_y), (face_x+face_w, face_y+face_h), (0, 255, 0), 3)
            
            # Save the captured image with face rectangle
            print("Saving face image")
            profileName = f"{studentInfo['Name']}_{utils.get_resultId():03}" + "Profile.jpg"
            cv2.imwrite(profileName, frame)
            
            # Ensure the static/Profiles directory exists
            print("Checking for Profiles directory")
            if not os.path.exists('static/Profiles'):
                os.makedirs('static/Profiles', exist_ok=True)
                print("Created Profiles directory")
            
            # Move the file to the Profiles folder
            print(f"Moving {profileName} to Profiles folder")
            result = utils.move_file_to_output_folder(profileName, 'Profiles')
            if not result:
                print("Failed to move file to Profiles folder")
                flash("Error saving profile image. Please try again.", category="error")
                cam.release()
                return redirect(url_for('faceInput'))
            
            # Release camera
            cam.release()
            
            # Reset camera for future use
            utils.cap = None
            
            # Restore the global flag for background processes
            utils.Globalflag = original_flag
            
            flash("Face captured successfully!", category="success")
            return redirect(url_for('confirmFaceInput'))
            
        except Exception as e:
            print(f"Error in face detection: {str(e)}")
            flash(f"Error detecting face: {str(e)}", category="error")
            cam.release()
            return redirect(url_for('faceInput'))
            
    except Exception as e:
        # Restore the global flag for background processes
        utils.Globalflag = original_flag if 'original_flag' in locals() else False
        
        if 'cam' in locals() and cam is not None and cam.isOpened():
            cam.release()
        flash(f"Error capturing face: {str(e)}", category="error")
        print(f"Error in saveFaceInput: {str(e)}")
        return redirect(url_for('faceInput'))

@app.route('/confirmFaceInput')
def confirmFaceInput():
    try:
        # Check if studentInfo exists
        if studentInfo is None:
            flash("Please login first before taking the exam", category="error")
            return redirect(url_for('main'))
        
        # Check if profileName exists
        if not profileName:
            flash("No face image captured. Please capture your face first.", category="error")
            return redirect(url_for('faceInput'))
            
        # Check if the profile image exists in the Profiles directory
        profile_path = os.path.join('static', 'Profiles', profileName)
        if not os.path.exists(profile_path):
            print(f"Profile image not found at {profile_path}")
            flash("Face image not found. Please capture your face again.", category="error")
            return redirect(url_for('faceInput'))
            
        # Check if the file is valid
        try:
            img = cv2.imread(profile_path)
            if img is None or img.size == 0:
                print(f"Image at {profile_path} is empty or invalid")
                flash("The captured image is invalid. Please try again.", category="error")
                return redirect(url_for('faceInput'))
        except Exception as e:
            print(f"Error reading image: {e}")
            flash("Error reading captured image. Please try again.", category="error")
            return redirect(url_for('faceInput'))
            
        # Create a direct path to confirm the image exists without the face recognition
        return render_template('ExamConfirmFaceInput.html', profile=profileName)
        
    except Exception as e:
        flash(f"Error confirming face input: {str(e)}", category="error")
        print(f"Error in confirmFaceInput: {str(e)}")
        return redirect(url_for('faceInput'))

@app.route('/systemCheck')
def systemCheck():
    return render_template('ExamSystemCheck.html')

@app.route('/systemCheck', methods=["POST"])
def systemCheckRoute():
    if request.method == 'POST':
        examData = request.json
        output = 'exam'
        if 'Not available' in examData['input'].split(';'): output = 'systemCheckError'
    return jsonify({"output": output})

@app.route('/systemCheckError')
def systemCheckError():
    return render_template('ExamSystemCheckError.html')

@app.route('/exam')
def exam():
    try:
        # Check if studentInfo exists
        if studentInfo is None:
            flash("Please login first before taking the exam", category="error")
            return redirect(url_for('main'))
            
        # Initialize the camera if not already done
        if not hasattr(utils, 'cap') or utils.cap is None or not utils.cap.isOpened():
            utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not utils.cap.isOpened():
                flash("Error: Could not open camera. Please check your camera connection.", category="error")
                return redirect(url_for('systemCheck'))
                
        # Hook keyboard shortcuts
        keyboard.hook(utils.shortcut_handler)
        return render_template('Exam.html')
    except Exception as e:
        flash(f"Error initializing exam: {str(e)}", category="error")
        return redirect(url_for('systemCheck'))

@app.route('/exam', methods=["POST"])
def examAction():
    # Check if studentInfo exists
    if studentInfo is None:
        return jsonify({"error": "User not logged in"}), 401
        
    link = ''
    if request.method == 'POST':
        examData = request.json
        if(examData['input']!=''):
            utils.Globalflag= False
            if hasattr(utils, 'cap') and utils.cap is not None and utils.cap.isOpened():
                utils.cap.release()
            utils.write_json({
                "Name": ('Prohibited Shorcuts (' + ','.join(list(dict.fromkeys(utils.shorcuts))) + ') are detected.'),
                "Time": (str(len(utils.shorcuts)) + " Counts"),
                "Duration": '',
                "Mark": (1.5 * len(utils.shorcuts)),
                "Link": '',
                "RId": utils.get_resultId()
            })
            utils.shorcuts=[]
            trustScore= utils.get_TrustScore(utils.get_resultId())
            totalMark=  math.floor(float(examData['input'])* 6.6667)
            if trustScore >=30:
                status="Fail(Cheating)"
                link = 'showResultFail'
            else:
                if totalMark < 50:
                    status="Fail"
                    link = 'showResultFail'
                else:
                    status="Pass"
                    link = 'showResultPass'
            utils.write_json({
                "Id": utils.get_resultId(),
                "Name": studentInfo['Name'],
                "TotalMark": totalMark,
                "TrustScore": max(100-trustScore, 0),
                "Status": status,
                "Date": time.strftime("%Y-%m-%d", time.localtime(time.time())),
                "StId": studentInfo['Id'],
                "Link" : profileName
            },"result.json")
            resultStatus= studentInfo['Name']+';'+str(totalMark)+';'+status+';'+time.strftime("%Y-%m-%d", time.localtime(time.time()))
        else:
            utils.Globalflag = True
            print('sfdsfsdsfdsfdsfdsfdsfdsfdsfds')
            resultStatus=''
    return jsonify({"output": resultStatus, "link": link})

@app.route('/showResultPass/<result_status>')
def showResultPass(result_status):
    return render_template('ExamResultPass.html',result_status=result_status)

@app.route('/showResultFail/<result_status>')
def showResultFail(result_status):
    return render_template('ExamResultFail.html',result_status=result_status)

#Admin Related
@app.route('/adminResults')
def adminResults():
    results = utils.getResults()
    return render_template('Results.html', results=results)

@app.route('/adminResultDetails/<resultId>')
def adminResultDetails(resultId):
    result_Details = utils.getResultDetails(resultId)
    return render_template('ResultDetails.html', resultDetials=result_Details)

@app.route('/adminResultDetailsVideo/<videoInfo>')
def adminResultDetailsVideo(videoInfo):
    return render_template('ResultDetailsVideo.html', videoInfo= videoInfo)

@app.route('/adminStudents')
def adminStudents():
    # Get all students from MongoDB
    students = list(students_collection.find({"Role": "STUDENT"}))
    return render_template('Students.html', students=students)

@app.route('/insertStudent', methods=['POST'])
def insertStudent():
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Get the highest ID currently in the collection
        highest_id = 0
        for student in students_collection.find({}, {"Id": 1}):
            if student.get("Id", 0) > highest_id:
                highest_id = student["Id"]
        
        # Insert new student with incremented ID
        students_collection.insert_one({
            "Id": highest_id + 1,
            "Name": name,
            "Email": email,
            "Password": password,
            "Role": "STUDENT"
        })
        return redirect(url_for('adminStudents'))

@app.route('/deleteStudent/<string:stdId>', methods=['GET'])
def deleteStudent(stdId):
    flash("Record Has Been Deleted Successfully")
    students_collection.delete_one({"Id": int(stdId)})
    return redirect(url_for('adminStudents'))

@app.route('/updateStudent', methods=['POST', 'GET'])
def updateStudent():
    if request.method == 'POST':
        id_data = int(request.form['id'])
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        students_collection.update_one(
            {"Id": id_data},
            {"$set": {
                "Name": name,
                "Email": email,
                "Password": password
            }}
        )
        return redirect(url_for('adminStudents'))

# Function to safely release resources
def cleanup_resources():
    global utils
    
    # Release camera if it exists
    if hasattr(utils, 'cap') and utils.cap is not None:
        try:
            if utils.cap.isOpened():
                utils.cap.release()
                print("Camera released")
        except Exception as e:
            print(f"Error releasing camera: {e}")
    
    # Set cap to None
    utils.cap = None
    
    # Reset flags
    utils.Globalflag = False
    
    # Allow some time for resources to be freed
    time.sleep(0.5)

@app.route('/cleanup', methods=['GET'])
def cleanup_route():
    """Route to manually trigger resource cleanup"""
    cleanup_resources()
    flash("Resources cleaned up successfully", "info")
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)