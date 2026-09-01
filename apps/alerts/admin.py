from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from .models import SecurityAlert


@admin.register(SecurityAlert)
class SecurityAlertAdmin(ModelAdmin):
    list_display = (
        'alert_id',
        'title',
        'camera',
        'get_severity_badge',
        'threat_score',
        'get_status_badge',
        'detected_object',
        'acknowledged_by',
        'created_at',
    )
    list_filter = (
        ('severity', ChoicesDropdownFilter),
        ('status', ChoicesDropdownFilter),
        ('camera', RelatedDropdownFilter),
    )
    search_fields = ('alert_id', 'title', 'description', 'detected_object', 'camera__camera_id', 'camera__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'acknowledged_at', 'resolved_at')

    fieldsets = (
        (
            'Alert Overview & Severity',
            {
                'classes': ['tab'],
                'fields': (
                    'alert_id',
                    'title',
                    'camera',
                    ('severity', 'threat_score'),
                    'status',
                ),
            },
        ),
        (
            'Threat Evidence & Details',
            {
                'classes': ['tab'],
                'fields': (
                    'detected_object',
                    'description',
                    'evidence_image',
                ),
            },
        ),
        (
            'Officer Dispatch & Resolution Audit',
            {
                'classes': ['tab'],
                'fields': (
                    'acknowledged_by',
                    ('acknowledged_at', 'resolved_at'),
                    'created_at',
                ),
            },
        ),
    )

    actions = [
        'mark_acknowledged',
        'mark_resolved',
        'reopen_alert',
    ]

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

    @display(
        description='Status',
        label={
            'ACTIVE': 'danger',
            'ACKNOWLEDGED': 'warning',
            'RESOLVED': 'success',
        }
    )
    def get_status_badge(self, obj):
        return obj.status

    @action(description='Acknowledge selected alerts (Assign to current officer)')
    def mark_acknowledged(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(
            status='ACKNOWLEDGED',
            acknowledged_by=request.user,
            acknowledged_at=now
        )
        self.message_user(request, f"{updated} alert(s) acknowledged by {request.user.username}.")

    @action(description='Resolve and clear selected alerts')
    def mark_resolved(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(
            status='RESOLVED',
            resolved_at=now
        )
        self.message_user(request, f"{updated} alert(s) marked as resolved.")

    @action(description='Reopen alerts (Set back to ACTIVE)')
    def reopen_alert(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f"{updated} alert(s) reopened.")
