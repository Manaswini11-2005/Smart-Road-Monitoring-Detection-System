import cv2
import os
import torch
import numpy as np
from ultralytics import YOLO
from django.conf import settings

# --- 1. Model Initialization ---
weights_path = os.path.join(settings.BASE_DIR, 'core/ai/weights/road_damage_yolov8.pt')
if not os.path.exists(weights_path):
    model = YOLO('yolov8s.pt') # Standard YOLOv8s
else:
    model = YOLO(weights_path) # Custom Weights (Detection or Segmentation)

def detect_damage(frame):
    if frame is None:
        return None, []
    
    # Pre-processing: Edge-Fusion for universal detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 1. AI Layer: YOLOv8
    # Increased confidence to 0.45 to reduce noise
    results = model(frame, conf=0.45, verbose=False) 
    detections = []
    
    # COCO Classes to ignore (if using base model): 0:person, 2:car, 3:motorcycle, 5:bus, 7:truck
    ignore_classes = [0, 2, 3, 5, 7]
    
    for result in results:
        if hasattr(result, 'masks') and result.masks is not None:
            for i, mask in enumerate(result.masks.xy):
                cls = int(result.boxes.cls[i])
                if cls in ignore_classes: continue # Filter out vehicles/people
                
                points = np.int32([mask])
                x, y, w, h = cv2.boundingRect(points)
                conf = float(result.boxes.conf[i])
                severity = classify_severity(frame[y:y+h, x:x+w])
                detections.append({'box': (x, y, x+w, y+h), 'label': 'AI-Pothole', 'confidence': conf, 'severity': severity})
        
        elif result.boxes is not None:
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls in ignore_classes: continue # Filter out vehicles/people
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                severity = classify_severity(frame[y1:y2, x1:x2])
                detections.append({'box': (x1, y1, x2, y2), 'label': 'AI-Pothole', 'confidence': conf, 'severity': severity})

    # 2. Universal CV Layer: Edge-Fusion & Contour Analysis
    height, width = frame.shape[:2]
    
    # Optimized ROI: Widen to capture side road areas but ignore car hood/dashboard
    mask = np.zeros_like(gray)
    roi_points = np.array([[
        (int(width * 0.05), int(height * 0.92)), # Bottom Left
        (int(width * 0.25), int(height * 0.45)), # Top Left
        (int(width * 0.75), int(height * 0.45)), # Top Right
        (int(width * 0.95), int(height * 0.92))  # Bottom Right
    ]], dtype=np.int32)
    cv2.fillPoly(mask, roi_points, 255)
    
    # Apply mask to the blurred image
    masked_roi = cv2.bitwise_and(blurred, blurred, mask=mask)
    
    # Canny Edge Detection (Resilient to color, sensitive to shape)
    edges = cv2.Canny(masked_roi, 60, 180) # Slightly higher thresholds
    
    # Sobel Gradient (Detects depth/volume changes)
    sobel_x = cv2.Sobel(masked_roi, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(masked_roi, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = cv2.magnitude(sobel_x, sobel_y)
    sobel_norm = cv2.normalize(sobel_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Fusion: Combine Shape (Edges) + Density (Sobel)
    fusion = cv2.addWeighted(edges, 0.4, sobel_norm, 0.6, 0)
    # Higher threshold (100) to ignore noise/wheel patterns
    _, binary = cv2.threshold(fusion, 100, 255, cv2.THRESH_BINARY)
    
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 800 < area < 40000:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Brightness Check: Ignore white/yellow lane markings
            # A pothole should be DARKER or similar to the road, not bright white
            crop = gray[y:y+h, x:x+w]
            avg_brightness = np.mean(crop)
            if avg_brightness > 170: # Typical white/yellow lines are > 200
                continue
            
            aspect_ratio = float(w)/h
            if 0.5 < aspect_ratio < 5.0:
                # Deduplication against AI
                duplicate = False
                for det in detections:
                    dx1, dy1, dx2, dy2 = det['box']
                    if abs(x - dx1) < 40 and abs(y - dy1) < 40:
                        duplicate = True; break
                
                if not duplicate:
                    severity = classify_severity(frame[y:y+h, x:x+w])
                    detections.append({
                        'box': (x, y, x+w, y+h),
                        'label': 'Pothole',
                        'confidence': 0.82,
                        'severity': severity
                    })

    # 3. Final Overlay
    for det in detections:
        x1, y1, x2, y2 = det['box']
        label, severity = det['label'], det['severity']
        # Futuristic Glow Theme
        color = (0, 0, 255) if severity == 'High' else (0, 215, 255) if severity == 'Medium' else (0, 255, 0)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        # Semi-transparent label background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1-30), (x1+180, y1), color, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        cv2.putText(frame, f"{label}: {severity}", (x1+5, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    return frame, detections

    return frame, detections

def classify_severity(crop):
    if crop.size == 0: return 'Low'
    h, w = crop.shape[:2]
    area = h * w
    if area > 12000: return 'High'
    elif area > 6000: return 'Medium'
    else: return 'Low'
