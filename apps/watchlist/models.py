from django.db import models

class WatchlistVehicle(models.Model):
    RISK_LEVELS = [
        ('CRITICAL', 'Critical Priority (Immediate Detain)'),
        ('HIGH', 'High Risk (Flag & Monitor)'),
        ('MEDIUM', 'Medium Risk (Secondary Inspection)'),
        ('LOW', 'Low Risk (Informational)'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active Flag'),
        ('Investigating', 'Under Investigation'),
        ('Resolved', 'Cleared / Inactive'),
    ]

    plate_number = models.CharField(max_length=30, unique=True)
    vehicle_type = models.CharField(max_length=50, default='Car')
    description = models.TextField(help_text="Reason for flagging (Sample/Demo data)")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='HIGH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    reported_sector = models.CharField(max_length=100, default='Sector 01 - Western Frontier')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-risk_level', '-created_at']

    def __str__(self):
        return f"{self.plate_number} - {self.risk_level} ({self.status})"
