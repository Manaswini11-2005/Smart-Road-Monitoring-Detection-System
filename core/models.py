from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RoadDamage(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    DAMAGE_TYPES = [
        ('Pothole', 'Pothole'),
        ('Crack', 'Crack'),
        ('Alligator Crack', 'Alligator Crack'),
        ('Other', 'Other'),
    ]

    detection_id = models.AutoField(primary_key=True)
    damage_type = models.CharField(max_length=50, choices=DAMAGE_TYPES, default='Pothole')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Low')
    confidence = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    image_path = models.ImageField(upload_to='detections/%Y/%m/%d/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.damage_type} - {self.severity} ({self.timestamp})"

    class Meta:
        verbose_name_plural = "Road Detections"
        ordering = ['-timestamp']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('Admin', 'Admin'), ('Driver', 'Driver')], default='Driver')

    def __str__(self):
        return self.user.username
