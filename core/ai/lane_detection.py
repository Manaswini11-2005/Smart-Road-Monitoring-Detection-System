import cv2
import numpy as np

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_img = cv2.bitwise_and(img, mask)
    return masked_img

def draw_lines(img, lines, color=[0, 255, 0], thickness=5):
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1 * (3 / 5))
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    if lines is None:
        return None
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]
        
        # STRICT SLOPE FILTERING: 
        # Left lane should be leaning left (negative slope), Right leaning right (positive)
        if -0.9 < slope < -0.3:
            left_fit.append((slope, intercept))
        elif 0.3 < slope < 0.9:
            right_fit.append((slope, intercept))
    
    left_fit_average = np.average(left_fit, axis=0) if left_fit else None
    right_fit_average = np.average(right_fit, axis=0) if right_fit else None
    
    averaged_lines = []
    if left_fit_average is not None:
        averaged_lines.append(make_coordinates(image, left_fit_average))
    if right_fit_average is not None:
        averaged_lines.append(make_coordinates(image, right_fit_average))
    
    return averaged_lines

def detect_lanes(frame):
    if frame is None:
        return None, {"status": "No Frame", "offset": 0}
    
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)

    # WIDE BUT RESTRICTED ROI: Skip horizon and sky to reduce noise
    roi_vertices = [
        (int(width * 0.05), height),         # Bottom Left
        (int(width * 0.40), int(height * 0.65)), # Top Left (Lowered to avoid horizon)
        (int(width * 0.60), int(height * 0.65)), # Top Right (Lowered to avoid horizon)
        (int(width * 0.95), height)          # Bottom Right
    ]
    vertices = np.array([roi_vertices], np.int32)
    masked_canny = region_of_interest(canny, vertices)

    lines = cv2.HoughLinesP(
        masked_canny,
        rho=2,
        theta=np.pi / 180,
        threshold=50, # Lower threshold for better sensitivity
        lines=np.array([]),
        minLineLength=30,
        maxLineGap=20 # Increased gap to handle dashed lines
    )

    lane_frame = frame.copy()
    averaged_lines = average_slope_intercept(frame, lines)
    
    lane_info = {"status": "Centered", "offset": 0}
    color = (0, 255, 0)
    
    if averaged_lines:
        for x1, y1, x2, y2 in averaged_lines:
            cv2.line(lane_frame, (x1, y1), (x2, y2), (0, 255, 0), 10)
        
        frame_center = width / 2
        
        if len(averaged_lines) == 2:
            lane_center = (averaged_lines[0][0] + averaged_lines[1][0]) / 2
            offset = lane_center - frame_center
            lane_info["offset"] = offset
        elif len(averaged_lines) == 1:
            # Single lane logic: Estimate offset based on typical lane position
            # If line is on the left, we expect the center to be to its right
            x1, y1, x2, y2 = averaged_lines[0]
            # Use the x-coordinate at the bottom of the frame
            lane_x = x1 
            
            # Simple heuristic: Typical lane width is ~400px at bottom of 640px frame
            if (x2 - x1) / (y2 - y1) < 0: # Left Lane (negative slope in image coords)
                estimated_center = lane_x + 200 # Assume center is 200px to the right
                lane_info["status"] = "Tracking Left Lane"
            else: # Right Lane
                estimated_center = lane_x - 200 # Assume center is 200px to the left
                lane_info["status"] = "Tracking Right Lane"
            
            offset = float(estimated_center - frame_center)
            lane_info["offset"] = offset
            color = (0, 255, 255) # Yellow for single line tracking
            
        # Determine drift/change status
        abs_offset = abs(float(lane_info["offset"]))
        if abs_offset > 80: # Increased threshold for "Change"
            lane_info["status"] = "Lane Change Detected"
            color = (0, 0, 255) # Red
        elif abs_offset > 40:
            lane_info["status"] = "Drifting " + ("Right" if float(lane_info["offset"]) > 0 else "Left")
            color = (0, 165, 255) # Orange
    else:
        lane_info["status"] = "No Lanes Detected"
        color = (255, 255, 255)

    # Draw Status Text with background for visibility
    cv2.putText(lane_frame, f"LANE: {lane_info['status']}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 3, cv2.LINE_AA)
    cv2.putText(lane_frame, f"OFFSET: {int(lane_info['offset'])}px", (50, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

    return lane_frame, lane_info
