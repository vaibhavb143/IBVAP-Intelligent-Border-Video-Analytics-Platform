from django.db import models
from apps.cameras.models import Camera

class SecurityEvent(models.Model):
    EVENT_TYPES = [
        ('INTRUSION', 'Restricted Zone Intrusion'),
        ('NIGHT_MOVEMENT', 'Night Movement Detected'),
        ('FRS_MATCH', 'Biometric FRS Watchlist Match'),
        ('ANPR_MATCH', 'Watchlist ANPR Match'),
        ('LOITERING', 'Perimeter Loitering & Reconnaissance'),
        ('CRAWLING_CONCEALMENT', 'Prone / Low-Crawl Infiltration Movement'),
        ('SUSPICIOUS_PACKAGE_DROP', 'Unattended Contraband / Object Drop'),
        ('CROWD_SURGE', 'Abnormal Crowd Clustering / Surge'),
        ('UNAUTHORIZED_VEHICLE', 'Unauthorized Vehicle Entry'),
        ('PERIMETER_CROSSING', 'Virtual Fence Crossing'),
    ]

    OBJECT_TYPES = [
        ('Person', 'Person / Pedestrian'),
        ('Vehicle', 'Motor Vehicle'),
        ('Package', 'Unattended Baggage / Contraband'),
        ('Animal', 'Animal / Wildlife'),
        ('Unknown', 'Unidentified Object'),
    ]

    SEVERITY_LEVELS = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    event_id = models.CharField(max_length=50, unique=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='INTRUSION')
    object_type = models.CharField(max_length=50, choices=OBJECT_TYPES, default='Person')
    threat_score = models.IntegerField(default=70)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='HIGH')
    
    # Evidence snapshot metadata
    evidence_image = models.CharField(max_length=300, blank=True)
    details = models.TextField(blank=True)
    confidence = models.FloatField(default=0.94)
    coordinates = models.CharField(max_length=100, default='32.7266 N, 74.8570 E')
    
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_id} - {self.get_event_type_display()} @ {self.camera.camera_id}"
