import cv2
import numpy as np
import time
import mediapipe as mp

def headMovmentDetection(image, face_mesh):
    print("Running HeadMovement Function")
    try:
        if image is None:
            print("Error: No image provided to headMovmentDetection")
            return
            
        # Flip the image horizontally for a later selfie-view display
        # Also convert the color space from BGR to RGB
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # To improve performance
        image.flags.writeable = False

        # Get the result with lower confidence thresholds
        results = face_mesh.process(image)

        # To improve performance
        image.flags.writeable = True

        # Convert the color space from RGB to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        img_h, img_w, img_c = image.shape
        face_3d = []
        face_2d = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        if idx == 1:
                            nose_2d = (lm.x * img_w, lm.y * img_h)
                            nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 8000)

                        x, y = int(lm.x * img_w), int(lm.y * img_h)

                        # Get the 2D Coordinates
                        face_2d.append([x, y])

                        # Get the 3D Coordinates
                        face_3d.append([x, y, lm.z])

                # Convert it to the NumPy array
                face_2d = np.array(face_2d, dtype=np.float64)

                # Convert it to the NumPy array
                face_3d = np.array(face_3d, dtype=np.float64)

                # The camera matrix
                focal_length = 1 * img_w

                cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                     [0, focal_length, img_w / 2],
                                     [0, 0, 1]])

                # The Distance Matrix
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # Solve PnP
                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                # Get rotational matrix
                rmat, jac = cv2.Rodrigues(rot_vec)

                # Get angles
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                # Get the y rotation degree
                x = angles[0] * 360
                y = angles[1] * 360
                
                # Adjusted thresholds for better detection
                textHead = ''
                if y < -8:  # Reduced from -10
                    textHead = "Looking Left"
                elif y > 12:  # Reduced from 15
                    textHead = "Looking Right"
                elif x < -6:  # Reduced from -8
                    textHead = "Looking Down"
                elif x > 12:  # Reduced from 15
                    textHead = "Looking Up"
                else:
                    textHead = "Forward"
                
                # Add the text on the image
                cv2.putText(image, textHead, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                Head_record_duration(textHead, image)
        else:
            print("No face landmarks detected")
            cv2.putText(image, "No face detected", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            Head_record_duration("No face detected", image)
            
    except Exception as e:
        print(f"Error in head movement detection: {str(e)}")
        cv2.putText(image, "Error in detection", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        Head_record_duration("Error in detection", image)

def cheat_Detection1():
    deleteTrashVideos()
    global Globalflag
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.3, min_tracking_confidence=0.3)  # Lowered thresholds
    print(f'CD1 Flag is {Globalflag}')
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera for cheat detection")
        return
        
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
    
    # Warm up camera
    for _ in range(10):  # Increased warmup frames
        success, _ = cap.read()
        if not success:
            print("Warmup frame failed")
        time.sleep(0.1)
        
    while Globalflag:
        try:
            success, image = cap.read()
            if not success:
                print("Failed to read frame from camera")
                time.sleep(0.1)
                continue
                
            if image is None:
                print("Received empty frame")
                time.sleep(0.1)
                continue
                
            headMovmentDetection(image, face_mesh)
        except Exception as e:
            print(f"Error in cheat_Detection1: {str(e)}")
            time.sleep(0.1)
            
    if Globalflag:
        cap.release()
    deleteTrashVideos()

def cheat_Detection2():
    global Globalflag, shorcuts
    print(f'CD2 Flag is {Globalflag}')

    deleteTrashVideos()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera for cheat detection")
        return
        
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Warm up camera
    for _ in range(5):
        cap.read()
        
    while Globalflag:
        try:
            success, image = cap.read()
            if not success:
                print("Failed to read frame from camera")
                time.sleep(0.1)
                continue
                
            if image is None:
                print("Received empty frame")
                time.sleep(0.1)
                continue
                
            image1 = image.copy()
            image2 = image.copy()
            MTOP_Detection(image1)
            screenDetection()
        except Exception as e:
            print(f"Error in cheat_Detection2: {str(e)}")
            time.sleep(0.1)
            
    deleteTrashVideos()
    if Globalflag:
        cap.release() 