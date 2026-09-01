from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.contrib.filters.admin import ChoicesDropdownFilter, DropdownFilter
from .models import Camera


@admin.register(Camera)
class CameraAdmin(ModelAdmin):
    list_display = (
        'camera_id',
        'name',
        'location',
        'get_status_badge',
        'get_threat_badge',
        'get_feed_badge',
        'is_ai_active',
        'people_count',
        'vehicle_count',
        'updated_at',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('threat_level', ChoicesDropdownFilter),
        ('feed_type', ChoicesDropdownFilter),
        ('source_type', ChoicesDropdownFilter),
        'is_ai_active',
    )
    search_fields = ('camera_id', 'name', 'location', 'source_url')
    ordering = ('camera_id',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (
            'Camera Feed & Connectivity',
            {
                'classes': ['tab'],
                'fields': (
                    'camera_id',
                    'name',
                    'location',
                    ('feed_type', 'source_type'),
                    'source_url',
                    'status',
                ),
            },
        ),
        (
            'Telemetry & Threat Status',
            {
                'classes': ['tab'],
                'fields': (
                    ('threat_level', 'is_ai_active'),
                    ('people_count', 'vehicle_count'),
                ),
            },
        ),
        (
            'AI Surveillance Modules',
            {
                'classes': ['tab'],
                'fields': (
                    'enable_human_detection',
                    'enable_vehicle_detection',
                    'enable_anpr',
                    'enable_frs',
                    'enable_intrusion_detection',
                    'enable_behavioral_analytics',
                    'enable_night_detection',
                ),
            },
        ),
        (
            'Geographical Coordinates',
            {
                'classes': ['tab'],
                'fields': (
                    ('latitude', 'longitude'),
                ),
            },
        ),
        (
            'Audit Timestamps',
            {
                'classes': ['tab'],
                'fields': (
                    ('created_at', 'updated_at'),
                ),
            },
        ),
    )

    actions = [
        'activate_ai',
        'deactivate_ai',
        'set_online',
        'set_standby',
        'set_offline',
    ]

    @display(
        description='Stream Status',
        label={
            'ONLINE': 'success',
            'STANDBY': 'warning',
            'OFFLINE': 'danger',
        }
    )
    def get_status_badge(self, obj):
        return obj.status

    @display(
        description='Threat Level',
        label={
            'CRITICAL': 'danger',
            'HIGH': 'warning',
            'ELEVATED': 'warning',
            'NORMAL': 'success',
        }
    )
    def get_threat_badge(self, obj):
        return obj.threat_level

    @display(
        description='Feed Type',
        label={
            'LIVE': 'info',
            'SIMULATION': 'primary',
        }
    )
    def get_feed_badge(self, obj):
        return obj.feed_type

    @action(description='Activate AI analytics on selected cameras')
    def activate_ai(self, request, queryset):
        updated = queryset.update(is_ai_active=True)
        self.message_user(request, f"AI analytics activated on {updated} camera feeds.")

    @action(description='Deactivate AI analytics on selected cameras')
    def deactivate_ai(self, request, queryset):
        updated = queryset.update(is_ai_active=False)
        self.message_user(request, f"AI analytics deactivated on {updated} camera feeds.")

    @action(description='Set status to ONLINE')
    def set_online(self, request, queryset):
        updated = queryset.update(status='ONLINE')
        self.message_user(request, f"{updated} cameras marked as ONLINE.")

    @action(description='Set status to STANDBY')
    def set_standby(self, request, queryset):
        updated = queryset.update(status='STANDBY')
        self.message_user(request, f"{updated} cameras marked as STANDBY.")

    @action(description='Set status to OFFLINE')
    def set_offline(self, request, queryset):
        updated = queryset.update(status='OFFLINE')
        self.message_user(request, f"{updated} cameras marked as OFFLINE.")
