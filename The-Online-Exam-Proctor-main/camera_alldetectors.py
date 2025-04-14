import cv2
import numpy as np

# Initialize face detector
face_net = cv2.dnn.readNetFromCaffe(
    "deploy.prototxt", 
    "res10_300x300_ssd_iter_140000.caffemodel"
)

# Initialize YOLO for object detection
yolo_net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
with open("coco.names", "r") as f:
    yolo_classes = [line.strip() for line in f.readlines()]
    
# Filter for prohibited objects (phones, books, etc.)
PROHIBITED_OBJECTS = ['cell phone', 'book', 'laptop', 'tv']

# Get output layer names for YOLO
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

# Initialize video capture
cap = cv2.VideoCapture(0)

# Confidence thresholds
FACE_CONFIDENCE = 0.7
OBJECT_CONFIDENCE = 0.5

def detect_faces(frame):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0)
    )
    
    face_net.setInput(blob)
    detections = face_net.forward()
    
    faces = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        
        if confidence > FACE_CONFIDENCE:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            faces.append((startX, startY, endX, endY))
    
    return faces

def detect_objects(frame):
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
    for i in indices:
        i = i
        class_name = yolo_classes[class_ids[i]]
        if class_name in PROHIBITED_OBJECTS:
            x, y, w, h = boxes[i]
            detected_objects.append((
                class_name,
                confidences[i],
                (x, y, x + w, y + h)
            ))
    
    return detected_objects

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    
    # Detect faces
    faces = detect_faces(frame)
    
    # Check for multiple faces
    if len(faces) > 1:
        cv2.putText(frame, "MULTIPLE FACES DETECTED!", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Draw face bounding boxes
    for (startX, startY, endX, endY) in faces:
        cv2.rectangle(frame, (startX, startY), (endX, endY),
                      (0, 255, 0), 2)
    
    # Detect prohibited objects
    objects = detect_objects(frame)
    
    # Draw object bounding boxes
    for (obj_type, confidence, (startX, startY, endX, endY)) in objects:
        cv2.rectangle(frame, (startX, startY), (endX, endY),
                      (0, 0, 255), 2)
        label = f"{obj_type}: {confidence:.2f}"
        cv2.putText(frame, label, (startX, startY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Show output
    cv2.imshow("Online Proctoring System", frame)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()