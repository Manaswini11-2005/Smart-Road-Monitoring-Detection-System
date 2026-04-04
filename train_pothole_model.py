import os
from ultralytics import YOLO

def train_custom_model():
    """
    Expert script to train YOLOv8 for Pothole Detection.
    Requirements:
    1. Install ultralytics: pip install ultralytics
    2. Prepare data.yaml with paths to your images and labels.
    """
    
    print("--- AI Pothole Detection Training Pipeline ---")
    
    # 1. Initialize a Small model (best balance of speed and accuracy for your project)
    model = YOLO('yolov8s.pt') 

    # 2. Define your data.yaml path
    # Make sure your data.yaml points to your training and validation images
    data_yaml_path = 'pothole_dataset/data.yaml' 
    
    if not os.path.exists(data_yaml_path):
        print(f"Error: {data_yaml_path} not found.")
        print("Please create a 'pothole_dataset' folder with 'data.yaml' and images/labels.")
        return

    # 3. Start training
    print("Starting training on your custom dataset...")
    results = model.train(
        data=data_yaml_path,
        epochs=50,         # Adjust epochs based on your dataset size
        imgsz=640,         # Standard size for pothole detection
        batch=16,          # Adjust based on your GPU memory
        name='pothole_model_v1',
        project='core/ai/runs',
        device='cpu'           # Changed from 0 to 'cpu' as no GPU was detected
    )

    print("Training Complete!")
    print("Your best model is saved at: core/ai/runs/pothole_model_v1/weights/best.pt")
    print("Move 'best.pt' to 'core/ai/weights/road_damage_yolov8.pt' to use it in the app!")

if __name__ == "__main__":
    train_custom_model()
