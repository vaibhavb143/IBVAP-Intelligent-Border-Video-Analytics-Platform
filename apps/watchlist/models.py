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


class WatchlistPerson(models.Model):
    THREAT_LEVELS = [
        ('CRITICAL', 'Critical (Immediate Intercept)'),
        ('HIGH', 'High Risk (Armed / Infiltrator)'),
        ('MEDIUM', 'Medium Risk (Suspected Smuggler)'),
        ('LOW', 'Low Risk (Person of Interest)'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active Wanted Notice'),
        ('Apprehended', 'Apprehended / Detained'),
        ('Investigating', 'Under Investigation'),
        ('Cleared', 'Cleared / Inactive'),
    ]

    CATEGORY_CHOICES = [
        ('INFILTRATOR', 'Cross-Border Infiltrator / Terrorist'),
        ('SMUGGLER', 'Contraband / Narcotics Smuggler'),
        ('SUSPECT', 'Wanted Criminal / Fugitive'),
        ('POW_DETAINEE', 'Escapee / Detainee of Interest'),
        ('PERSON_OF_INTEREST', 'General Person of Interest'),
    ]

    person_id = models.CharField(max_length=50, unique=True, help_text="e.g. FRS-IND-042")
    full_name = models.CharField(max_length=150)
    alias = models.CharField(max_length=150, blank=True, help_text="Known aliases or callsigns")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='INFILTRATOR')
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS, default='HIGH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    facial_embedding_id = models.CharField(max_length=100, blank=True, help_text="AI Feature Vector / Embedding Hash")
    last_seen_sector = models.CharField(max_length=150, default='Sector 01 - Forward Outpost Alpha')
    reason_for_flagging = models.TextField(help_text="Intelligence dossier notes / reason for biometric watchlist entry")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-threat_level', '-created_at']

    def __str__(self):
        return f"[{self.threat_level}] {self.full_name} ({self.person_id})"
