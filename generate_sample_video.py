import cv2
import numpy as np
import os

def create_sample_video():
    # Define video properties
    width, height = 640, 480
    fps = 20
    duration = 15 # seconds
    output_path = r'c:\Users\akash\OneDrive\Desktop\NEW 2026 PROJECT DEVELOPMENT\Ai car with real time detection of damaged road and lane detection\core\static\videos\lane_pothole_demo.mp4'
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Generate frames
    for i in range(fps * duration):
        frame = np.full((height, width, 3), 100, dtype=np.uint8)
        
        # Lane Drift Logic
        # Shift the whole road perspective horizontally over time
        drift = int(100 * np.sin(i / (fps * 3))) # Drift left and right every 3 seconds
        
        left_x1, left_x2 = 200 + drift, 300 + drift//2
        right_x1, right_x2 = 440 + drift, 340 + drift//2
        
        cv2.line(frame, (left_x1, height), (left_x2, 200), (255, 255, 255), 5)
        cv2.line(frame, (right_x1, height), (right_x2, 200), (255, 255, 255), 5)
        
        # Potholes
        pothole_points = [
            (320, 300, 10),  # x, y_start, frame_offset
            (250, 400, 80),
            (400, 350, 150),
            (300, 250, 220)
        ]
        
        for px, py_start, offset in pothole_points:
            local_i = i - offset
            if local_i > 0:
                p_y = py_start + (local_i * 10) % (height - py_start)
                p_x = px + drift # Pothole moves with the road drift
                
                if py_start < p_y < height:
                    cv2.ellipse(frame, (p_x, p_y), (40, 20), 0, 0, 360, (50, 50, 50), -1)
                    cv2.putText(frame, "POTHOLE", (p_x - 30, p_y - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        out.write(frame)
        
    out.release()
    print(f"Integrated demo video created at: {output_path}")

if __name__ == "__main__":
    create_sample_video()
