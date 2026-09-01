from django.db import models

class Camera(models.Model):
    FEED_TYPE_CHOICES = [
        ('LIVE', 'LIVE — WEBCAM'),
        ('SIMULATION', 'SIMULATION — VIDEO'),
    ]

    SOURCE_TYPE_CHOICES = [
        ('WEBCAM', 'Local Laptop Webcam / USB'),
        ('VIDEO_FILE', 'Simulated Border Video Asset'),
        ('RTSP_STREAM', 'RTSP / Network CCTV Feed'),
    ]

    STATUS_CHOICES = [
        ('ONLINE', 'Online / Operational'),
        ('STANDBY', 'Standby'),
        ('OFFLINE', 'Offline / Connection Lost'),
    ]

    THREAT_CHOICES = [
        ('NORMAL', 'Normal'),
        ('ELEVATED', 'Elevated'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    camera_id = models.CharField(max_length=50, unique=True, help_text="e.g. BOP-01, GATE-01")
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200, help_text="e.g. Sector 01 - Forward Post Alpha")
    feed_type = models.CharField(max_length=20, choices=FEED_TYPE_CHOICES, default='SIMULATION')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='VIDEO_FILE')
    source_url = models.CharField(max_length=500, blank=True, help_text="RTSP URL, file path, or device index 0")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ONLINE')
    
    # Live counts (Sample/Simulated/Live telemetry)
    people_count = models.IntegerField(default=0)
    vehicle_count = models.IntegerField(default=0)
    is_ai_active = models.BooleanField(default=True)
    threat_level = models.CharField(max_length=20, choices=THREAT_CHOICES, default='NORMAL')

    # AI Module Toggles
    enable_human_detection = models.BooleanField(default=True, verbose_name="Human Detection")
    enable_vehicle_detection = models.BooleanField(default=True, verbose_name="Vehicle Classification")
    enable_anpr = models.BooleanField(default=False, verbose_name="ANPR / OCR")
    enable_frs = models.BooleanField(default=True, verbose_name="Facial Recognition (FRS)")
    enable_intrusion_detection = models.BooleanField(default=True, verbose_name="Virtual Fence Intrusion")
    enable_behavioral_analytics = models.BooleanField(default=True, verbose_name="Behavioral / Activity Analytics")
    enable_night_detection = models.BooleanField(default=True, verbose_name="Night-Time Vision / Movement")

    # Map Coordinates
    latitude = models.FloatField(default=32.7266)
    longitude = models.FloatField(default=74.8570)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['camera_id']

    def __str__(self):
        return f"{self.camera_id} - {self.name} ({self.get_feed_type_display()})"
