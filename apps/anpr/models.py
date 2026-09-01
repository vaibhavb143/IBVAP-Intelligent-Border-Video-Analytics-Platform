from django.db import models
from apps.cameras.models import Camera

class ANPRDetection(models.Model):
    VEHICLE_TYPES = [
        ('Car', 'Sedan / Hatchback'),
        ('SUV', 'SUV / 4x4 Off-road'),
        ('Truck', 'Commercial Heavy Truck'),
        ('Motorcycle', 'Motorcycle / Two-Wheeler'),
        ('Bus', 'Transport Bus'),
        ('Van', 'Cargo / Delivery Van'),
    ]

    MATCH_STATUS = [
        ('MATCH', 'Watchlist Match Flagged'),
        ('CLEARED', 'Normal / Non-Watchlist'),
        ('FLAGGED', 'Suspicious / OCR Unverified'),
    ]

    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='anpr_detections')
    plate_number = models.CharField(max_length=30, db_index=True)
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPES, default='Car')
    confidence = models.FloatField(default=0.95, help_text="OCR Confidence Score (0.00 to 1.00)")
    is_watchlist_match = models.BooleanField(default=False)
    match_status = models.CharField(max_length=20, choices=MATCH_STATUS, default='CLEARED')
    watchlist_risk = models.CharField(max_length=20, default='NORMAL')
    
    speed_estimate = models.CharField(max_length=50, default='42 km/h')
    direction = models.CharField(max_length=50, default='Inbound (Gate 1 -> Zone B)')
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.plate_number} ({self.vehicle_type}) - {self.camera.camera_id}"
