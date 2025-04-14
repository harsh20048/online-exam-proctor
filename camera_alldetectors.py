import cv2
import numpy as np
import os

# Global variables
use_dnn = False
use_yolo = False
face_net = None
yolo_net = None
yolo_classes = []
output_layers = []

# Initialize face detectors
try:
    # Try to load DNN model
    face_net = cv2.dnn.readNetFromCaffe(
        "deploy.prototxt", 
        "res10_300x300_ssd_iter_140000.caffemodel"
    )
    # Test if model loaded correctly
    test_blob = cv2.dnn.blobFromImage(np.zeros((300, 300, 3), np.uint8))
    face_net.setInput(test_blob)
    face_net.forward()
    use_dnn = True
    print("DNN face detector initialized successfully")
except Exception as e:
    print(f"Warning: Could not load DNN face detector ({str(e)}), falling back to Haar cascade")
    use_dnn = False

# Load Haar cascade
try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        raise ValueError("Failed to load face cascade classifier")
    print("Haar cascade classifier loaded successfully")
except Exception as e:
    print(f"Error: Could not load face cascade classifier: {str(e)}")
    exit(1)

# Initialize YOLO for object detection
try:
    if os.path.exists("yolov3.weights") and os.path.exists("yolov3.cfg") and os.path.exists("coco.names"):
        yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        with open("coco.names", "r") as f:
            yolo_classes = [line.strip() for line in f.readlines()]
            
        # Get output layer names for YOLO
        layer_names = yolo_net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]
        
        # Test YOLO initialization
        test_blob = cv2.dnn.blobFromImage(np.zeros((416, 416, 3), np.uint8))
        yolo_net.setInput(test_blob)
        yolo_net.forward(output_layers)
        use_yolo = True
        print("YOLO object detector initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize YOLO object detector: {str(e)}")
    use_yolo = False
    
# Filter for prohibited objects (phones, books, etc.)
PROHIBITED_OBJECTS = ['cell phone', 'book', 'laptop', 'tv']

# Initialize video capture
cap = None
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Try with DSHOW
        
    if not cap.isOpened():
        raise ValueError("Could not open camera")
        
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    print("Camera initialized successfully")
except Exception as e:
    print(f"Error: Failed to initialize camera: {str(e)}")
    exit(1)

# Confidence thresholds
FACE_CONFIDENCE = 0.3  # Lowered for better detection
OBJECT_CONFIDENCE = 0.5

def preprocess_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE with better parameters
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # Apply bilateral filter with better parameters
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    
    # Apply adaptive thresholding with better parameters
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY, 11, 2)
    
    # Apply morphological operations to enhance features
    kernel = np.ones((3,3), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    
    return gray

def detect_faces_dnn(frame):
    try:
        (h, w) = frame.shape[:2]
        
        # Preprocess frame
        gray = preprocess_frame(frame)
        
        # Convert back to BGR for DNN
        frame_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Create multiple scales for better detection
        scales = [0.7, 0.85, 1.0, 1.15, 1.3]
        all_faces = []
        
        for scale in scales:
            resized = cv2.resize(frame_rgb, (int(300 * scale), int(300 * scale)))
            blob = cv2.dnn.blobFromImage(
                resized, 1.0, (300, 300),
                (104.0, 177.0, 123.0)
            )
            
            face_net.setInput(blob)
            detections = face_net.forward()
            
            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > FACE_CONFIDENCE:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    # Scale back coordinates
                    startX = int(startX / scale)
                    startY = int(startY / scale)
                    endX = int(endX / scale)
                    endY = int(endY / scale)
                    
                    # Ensure coordinates are within frame bounds
                    startX = max(0, startX)
                    startY = max(0, startY)
                    endX = min(w, endX)
                    endY = min(h, endY)
                    
                    # Validate face size and aspect ratio
                    face_width = endX - startX
                    face_height = endY - startY
                    
                    if (face_width > 35 and face_height > 35 and  # Reduced minimum size
                        0.3 < face_width/face_height < 3.0):  # More lenient aspect ratio
                        
                        # Calculate face center
                        center_x = (startX + endX) // 2
                        center_y = (startY + endY) // 2
                        
                        # Check if this face overlaps with any existing face
                        is_overlapping = False
                        for existing_face in all_faces:
                            ex1, ey1, ex2, ey2 = existing_face
                            # Calculate overlap
                            x1 = max(startX, ex1)
                            y1 = max(startY, ey1)
                            x2 = min(endX, ex2)
                            y2 = min(endY, ey2)
                            
                            if x1 < x2 and y1 < y2:  # If there's overlap
                                # Calculate overlap area
                                overlap_area = (x2 - x1) * (y2 - y1)
                                face1_area = (endX - startX) * (endY - startY)
                                face2_area = (ex2 - ex1) * (ey2 - ey1)
                                
                                # If overlap is significant, skip this face
                                if overlap_area > 0.3 * min(face1_area, face2_area):
                                    is_overlapping = True
                                    break
                        
                        if not is_overlapping:
                            all_faces.append((startX, startY, endX, endY))
        
        return all_faces
    except Exception as e:
        print(f"Error in DNN face detection: {str(e)}")
        return []

def detect_faces_haar(frame):
    try:
        # Preprocess frame
        gray = preprocess_frame(frame)
        
        # Try multiple scales for better detection
        scales = [0.7, 0.85, 1.0, 1.15, 1.3]
        all_faces = []
        
        for scale in scales:
            resized = cv2.resize(gray, (int(gray.shape[1] * scale), int(gray.shape[0] * scale)))
            
            faces = face_cascade.detectMultiScale(
                resized,
                scaleFactor=1.05,
                minNeighbors=2,
                minSize=(35, 35),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            for (x, y, w, h) in faces:
                # Scale back coordinates
                x = int(x / scale)
                y = int(y / scale)
                w = int(w / scale)
                h = int(h / scale)
                
                # Validate face size and aspect ratio
                if (w > 35 and h > 35 and  # Reduced minimum size
                    0.3 < w/h < 3.0):  # More lenient aspect ratio
                    
                    # Check if this face overlaps with any existing face
                    is_overlapping = False
                    for existing_face in all_faces:
                        ex, ey, ew, eh = existing_face
                        # Calculate overlap
                        x1 = max(x, ex)
                        y1 = max(y, ey)
                        x2 = min(x + w, ex + ew)
                        y2 = min(y + h, ey + eh)
                        
                        if x1 < x2 and y1 < y2:  # If there's overlap
                            # Calculate overlap area
                            overlap_area = (x2 - x1) * (y2 - y1)
                            face1_area = w * h
                            face2_area = ew * eh
                            
                            # If overlap is significant, skip this face
                            if overlap_area > 0.3 * min(face1_area, face2_area):
                                is_overlapping = True
                                break
                    
                    if not is_overlapping:
                        all_faces.append((x, y, x + w, y + h))
        
        return all_faces
    except Exception as e:
        print(f"Error in Haar face detection: {str(e)}")
        return []

def detect_faces(frame):
    all_faces = []
    
    # Try DNN first if available
    if use_dnn:
        dnn_faces = detect_faces_dnn(frame)
        if dnn_faces:  # If DNN detection successful
            all_faces.extend(dnn_faces)
    
    # Always try Haar cascade as well
    haar_faces = detect_faces_haar(frame)
    
    # Combine and remove duplicates
    for haar_face in haar_faces:
        # Check if this face is already detected by DNN
        is_duplicate = False
        for dnn_face in all_faces:
            # Calculate overlap
            x1 = max(haar_face[0], dnn_face[0])
            y1 = max(haar_face[1], dnn_face[1])
            x2 = min(haar_face[2], dnn_face[2])
            y2 = min(haar_face[3], dnn_face[3])
            
            if x1 < x2 and y1 < y2:  # If there's overlap
                # Calculate overlap area
                overlap_area = (x2 - x1) * (y2 - y1)
                face1_area = (haar_face[2] - haar_face[0]) * (haar_face[3] - haar_face[1])
                face2_area = (dnn_face[2] - dnn_face[0]) * (dnn_face[3] - dnn_face[1])
                
                # If overlap is significant, skip this face
                if overlap_area > 0.3 * min(face1_area, face2_area):
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            all_faces.append(haar_face)
    
    return all_faces

def detect_objects(frame):
    if not use_yolo:
        return []
        
    try:
        height, width = frame.shape[:2]
        
        # Prepare frame for YOLO
        blob = cv2.dnn.blobFromImage(
            frame, 0.00392, (416, 416), (0, 0, 0), 
            True, crop=False
        )
        yolo_net.setInput(blob)
        outs = yolo_net.forward(output_layers)
        
        # Process YOLO output
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > OBJECT_CONFIDENCE:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-max suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, OBJECT_CONFIDENCE, 0.4)
        
        detected_objects = []
        if len(indices) > 0:
            for i in indices.flatten():
                class_name = yolo_classes[class_ids[i]]
                if class_name in PROHIBITED_OBJECTS:
                    x, y, w, h = boxes[i]
                    detected_objects.append((
                        class_name,
                        confidences[i],
                        (x, y, x + w, y + h)
                    ))
        
        return detected_objects
    except Exception as e:
        print(f"Warning: Object detection failed: {str(e)}")
        return []

try:
    print("Starting camera feed. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect faces
        faces = detect_faces(frame)
        
        # Check for multiple faces
        if len(faces) > 1:
            cv2.putText(frame, f"MULTIPLE FACES DETECTED! ({len(faces)} faces)", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        elif len(faces) == 0:
            cv2.putText(frame, "NO FACE DETECTED!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Face Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw face bounding boxes with different colors for multiple faces
        for i, (startX, startY, endX, endY) in enumerate(faces):
            # Use different colors for different faces
            color = (0, 255, 0) if len(faces) == 1 else (0, 255, 255) if i == 0 else (255, 0, 0)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            
            # Add face number for multiple faces
            if len(faces) > 1:
                cv2.putText(frame, f"Face {i+1}", (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Detect prohibited objects
        objects = detect_objects(frame)
        
        # Draw object bounding boxes
        for (obj_type, confidence, (startX, startY, endX, endY)) in objects:
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          (0, 0, 255), 2)
            label = f"{obj_type}: {confidence:.2f}"
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Show output
        cv2.imshow("Online Proctoring System", frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

except Exception as e:
    print(f"Error in main loop: {str(e)}")
    
finally:
    # Clean up
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    print("Cleanup completed")