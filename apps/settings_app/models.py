from django.db import models

class SystemConfiguration(models.Model):
    # Night Detection Window
    night_start_time = models.CharField(max_length=10, default='22:00')
    night_end_time = models.CharField(max_length=10, default='05:00')

    # Threat Scoring Weights (Demo/Prototype values)
    weight_person_detection = models.IntegerField(default=20)
    weight_night_movement = models.IntegerField(default=15)
    weight_restricted_zone = models.IntegerField(default=30)
    weight_loitering = models.IntegerField(default=10)
    weight_watchlist_vehicle = models.IntegerField(default=40)

    # General Preferences
    auto_refresh_rate = models.IntegerField(default=5, help_text="Stream sync interval in seconds")
    audio_alerts = models.BooleanField(default=True)
    high_threat_threshold = models.IntegerField(default=75)
    
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_settings(cls):
        config, _ = cls.objects.get_or_create(id=1)
        return config

    def __str__(self):
        return f"IBVAP System Settings (Updated {self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else 'Default'})"
