from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SystemConfiguration


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(ModelAdmin):
    list_display = (
        '__str__',
        'night_start_time',
        'night_end_time',
        'high_threat_threshold',
        'auto_refresh_rate',
        'audio_alerts',
        'updated_at',
    )
    readonly_fields = ('updated_at',)

    fieldsets = (
        (
            'Night Vision & Thermal Schedule Window',
            {
                'classes': ['tab'],
                'fields': (
                    ('night_start_time', 'night_end_time'),
                ),
            },
        ),
        (
            'Threat Scoring Model Weights',
            {
                'classes': ['tab'],
                'fields': (
                    'weight_person_detection',
                    'weight_night_movement',
                    'weight_restricted_zone',
                    'weight_loitering',
                    'weight_watchlist_vehicle',
                ),
            },
        ),
        (
            'Surveillance Interface & Telemetry Preferences',
            {
                'classes': ['tab'],
                'fields': (
                    ('auto_refresh_rate', 'high_threat_threshold'),
                    'audio_alerts',
                    'updated_at',
                ),
            },
        ),
    )
