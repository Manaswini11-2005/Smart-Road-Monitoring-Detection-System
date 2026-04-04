# Execution Guide: AI-Based Smart Vehicle System

## 1. Prerequisites
- Python 3.9+
- MySQL 8.0 Server
- Graphics Driver (for YOLO/TensorFlow acceleration)

## 2. Installation
```bash
# Clone the repository (or navigate to directory)
cd "Ai car with real time detection..."

# Install dependencies
pip install -r requirements.txt
```

## 3. Database Setup (MySQL)
1. Open MySQL Command Line or Workbench.
2. Run the following:
```sql
CREATE DATABASE smart_vehicle_db;
-- Note: Settings are configured for 'root' with no password. 
-- Update smart_vehicle_project/settings.py if your credentials differ.
```

## 4. Run Migrations
```bash
python manage.py makemigrations core
python manage.py migrate
```

## 5. Training Guide
### YOLOv8 (Road Damage)
1. Download a dataset (e.g., [RDD2020 on Roboflow](https://roboflow.com/)).
2. Use the following command to train:
```bash
yolo task=detect mode=train model=yolov8n.pt data=custom_data.yaml epochs=50 imgsz=640
```
3. Copy the resulting `best.pt` to `core/ai/weights/road_damage_yolov8.pt`.

### CNN (Severity)
- Use the `classify_severity` placeholder in `core/ai/damage_detection.py` or load a pre-trained Keras model using `tensorflow.keras.models.load_model()`.

## 6. Launch Application
```bash
python manage.py runserver
```
- **Dashboard:** `http://127.0.0.1:8000/`
- **Live Feed:** `http://127.0.0.1:8000/live/`

## 7. Retraining Simulation
```bash
python manage.py retrain
```
