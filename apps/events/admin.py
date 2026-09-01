from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from .models import SecurityEvent


@admin.register(SecurityEvent)
class SecurityEventAdmin(ModelAdmin):
    list_display = (
        'event_id',
        'camera',
        'get_event_type_badge',
        'object_type',
        'get_severity_badge',
        'threat_score',
        'get_confidence_formatted',
        'timestamp',
    )
    list_filter = (
        ('event_type', ChoicesDropdownFilter),
        ('severity', ChoicesDropdownFilter),
        ('camera', RelatedDropdownFilter),
        ('object_type', ChoicesDropdownFilter),
    )
    search_fields = ('event_id', 'details', 'coordinates', 'camera__camera_id', 'camera__name')
    ordering = ('-timestamp',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (
            'Event Classification & Threat Rating',
            {
                'classes': ['tab'],
                'fields': (
                    'event_id',
                    'camera',
                    ('event_type', 'object_type'),
                    ('severity', 'threat_score'),
                ),
            },
        ),
        (
            'AI Detection Evidence & Location',
            {
                'classes': ['tab'],
                'fields': (
                    ('confidence', 'coordinates'),
                    'evidence_image',
                    'details',
                ),
            },
        ),
        (
            'Timestamp Logs',
            {
                'classes': ['tab'],
                'fields': (
                    'timestamp',
                    'created_at',
                ),
            },
        ),
    )

    @display(
        description='Event Type',
        label={
            'INTRUSION': 'danger',
            'NIGHT_MOVEMENT': 'warning',
            'ANPR_MATCH': 'danger',
            'LOITERING': 'warning',
            'UNAUTHORIZED_VEHICLE': 'warning',
            'PERIMETER_CROSSING': 'danger',
        }
    )
    def get_event_type_badge(self, obj):
        return obj.event_type

    @display(
        description='Severity',
        label={
            'CRITICAL': 'danger',
            'HIGH': 'warning',
            'MEDIUM': 'info',
            'LOW': 'success',
        }
    )
    def get_severity_badge(self, obj):
        return obj.severity

    @display(description='AI Confidence')
    def get_confidence_formatted(self, obj):
        return f"{obj.confidence * 100:.1f}%"
