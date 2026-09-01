from django.db import models
from django.contrib.auth.models import User
from apps.cameras.models import Camera

class SecurityAlert(models.Model):
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active / Unresolved'),
        ('ACKNOWLEDGED', 'Acknowledged by Officer'),
        ('RESOLVED', 'Resolved & Cleared'),
    ]

    alert_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='HIGH')
    threat_score = models.IntegerField(default=75, help_text="Calculated risk value 0-100")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    detected_object = models.CharField(max_length=100, default='Person')
    description = models.TextField(blank=True)
    evidence_image = models.CharField(max_length=300, blank=True, help_text="Path or SVG visual representation")
    
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title} @ {self.camera.camera_id} ({self.status})"
