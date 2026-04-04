# Running the Smart Vehicle AI System

Follow these steps to set up and run the AI-powered lane and pothole detection system.

## 1. Prerequisites
- **Python 3.10+** installed on your system.
- **Microphone & Speakers** (for voice alerts).
- **GPU (Optional)**: If you have an NVIDIA GPU with CUDA, YOLOv8 will run significantly faster.

## 2. Installation
Open your terminal in the project directory and run:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Database Migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create Admin Account (Optional, to access /admin)
python manage.py createsuperuser
```

## 3. Launching the System
```bash
python manage.py runserver
```
Once the server is running, open your browser and navigate to:
**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

## 4. Using the Detection Features
1. **Live Feed**: Go to the "Live Feed" page.
2. **Upload/Stream**: The system will automatically begin processing the default video stream or the uploaded file.
3. **Voice Alerts**: Ensure your volume is up. You will hear:
   - *"Warning: Pothole detected ahead!"* for road hazards.
   - *"Warning: Vehicle drifting from lane!"* for lane departures.
4. **Dashboard**: Observe the "Neural Stream" for real-time AI bounding boxes and lane status indicators.

## 5. Helpful Scripts
- **Download Samples**: `python download_test_samples.py` to get high-quality road videos.
- **Retrain AI**: `python train_pothole_model.py` to start a new training session with your own data.
- **Generate Demo**: `python generate_sample_video.py` to create a synthetic video for offline testing.

---
**Note**: If the web-browser shows "No Video Stream", ensure you have allowed the browser to access your camera or that the video file path in `core/views.py` is correct.
