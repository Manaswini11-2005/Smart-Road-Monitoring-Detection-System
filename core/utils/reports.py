import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from core.models import RoadDamage

def generate_pdf_report():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 750, "Smart Vehicle Road Damage Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Generated on: {RoadDamage.objects.all().order_by('-timestamp').first().timestamp if RoadDamage.objects.exists() else 'N/A'}")
    
    y = 700
    p.drawString(100, y, "ID | Type | Severity | Confidence | Latitude | Longitude")
    y -= 20
    
    detections = RoadDamage.objects.all()[:20] # Last 20
    for det in detections:
        line = f"#{det.detection_id} | {det.damage_type} | {det.severity} | {det.confidence:.2f} | {det.latitude} | {det.longitude}"
        p.drawString(100, y, line)
        y -= 15
        if y < 50:
            p.showPage()
            y = 750
            
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
