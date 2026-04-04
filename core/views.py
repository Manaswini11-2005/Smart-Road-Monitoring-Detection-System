import cv2
import time
import json
import os
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.generic import TemplateView, ListView
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from core.models import RoadDamage
from .ai.lane_detection import detect_lanes
from .ai.damage_detection import detect_damage
from .utils.voice_alerts import notify_pothole, notify_lane_departure

class VideoCamera:
    def __init__(self, source=0):
        self.video = cv2.VideoCapture(source)
        self.source = source
        self.last_detection_time = 0.0
        self.last_lane_alert_time = 0.0

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            if isinstance(self.source, str) and os.path.exists(self.source):
                # Loop video simulation
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = self.video.read()
            else:
                return None
        
        if frame is None:
            return None

        # Apply AI
        frame, lane_info = detect_lanes(frame)
        frame, detections = detect_damage(frame)

        # Handle lane alerts
        if lane_info["status"] in ["Drifting Left", "Drifting Right", "Lane Change/Partial Lane"]:
            if time.time() - self.last_lane_alert_time > 5.0:  # 5 second throttle for lane alerts
                self.last_lane_alert_time = time.time()
                notify_lane_departure()

        # Handle damage alerts and database logging
        if detections and (time.time() - self.last_detection_time > 0.5):
            self.last_detection_time = time.time()
            for det in detections:
                if det['confidence'] > 0.3:
                    # Save to DB
                    RoadDamage.objects.create(
                        damage_type='Pothole',
                        severity=det['severity'],
                        confidence=det['confidence'],
                        # Mock GPS (Can be extended with actual GPS sensor data)
                        latitude=12.9716, 
                        longitude=77.5946 
                    )
                    if det['severity'] in ['High', 'Medium']:
                        notify_pothole(det['severity'])

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

from django.views.decorators.csrf import csrf_exempt
import glob

def get_latest_video():
    video_dir = os.path.join(settings.BASE_DIR, 'core/static/videos')
    files = glob.glob(os.path.join(video_dir, '*.mp4'))
    if not files:
        return 0 # Default to camera
    # Sort files by modification time, descending
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def video_feed(request):
    source = get_latest_video()
    return StreamingHttpResponse(gen(VideoCamera(source)),
                                content_type='multipart/x-mixed-replace; boundary=frame')

class LiveView(TemplateView):
    template_name = 'core/live.html'

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
    # ... existing get_context_data code ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_detections = RoadDamage.objects.all()
        context['total_detections'] = all_detections.count()
        context['potholes_list'] = all_detections.order_by('-timestamp')[:50]
        
        if context['total_detections'] == 0:
            score = 100
        else:
            high_sev = all_detections.filter(severity='High').count()
            med_sev = all_detections.filter(severity='Medium').count()
            low_sev = all_detections.filter(severity='Low').count()
            penalty = (high_sev * 15) + (med_sev * 7) + (low_sev * 3)
            score = max(0, 100 - penalty)
        
        context['road_health_score'] = score
        context['health_status'] = "Excellent" if score > 90 else "Good" if score > 75 else "Fair" if score > 50 else "Poor"
        context['health_color'] = "success" if score > 75 else "warning" if score > 50 else "danger"
        
        type_counts = RoadDamage.objects.values('damage_type').annotate(count=Count('damage_type'))
        context['type_labels'] = [x['damage_type'] for x in type_counts]
        context['type_data'] = [x['count'] for x in type_counts]
        severity_counts = RoadDamage.objects.values('severity').annotate(count=Count('severity'))
        context['severity_labels'] = [x['severity'] for x in severity_counts]
        context['severity_data'] = [x['count'] for x in severity_counts]
        return context

class ResultsListView(ListView):
    model = RoadDamage
    template_name = 'core/results.html'
    context_object_name = 'detections'
    paginate_by = 10

from .utils.reports import generate_pdf_report
from django.http import HttpResponse

def export_report_pdf(request):
    pdf_buffer = generate_pdf_report()
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Road_Damage_Report.pdf"'
    return response

def mobile_api_upload(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'Image received'})
    return JsonResponse({'error': 'POST required'})

@csrf_exempt
def video_upload(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        video_file = request.FILES['video_file']
        if video_file.name.endswith('.mp4'):
            # Save with timestamped name to prevent Windows file locking errors
            ts = int(time.time())
            filename = f"upload_{ts}.mp4"
            upload_path = os.path.join(settings.BASE_DIR, f'core/static/videos/{filename}')
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            return JsonResponse({'status': 'success', 'message': 'Video uploaded successfully!'})
        return JsonResponse({'status': 'error', 'message': 'Only MP4 files are supported.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
