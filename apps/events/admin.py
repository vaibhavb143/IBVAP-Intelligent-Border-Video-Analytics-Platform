from django.contrib import admin
from .models import SecurityEvent

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'camera', 'event_type', 'object_type', 'threat_score', 'severity', 'timestamp')
    list_filter = ('event_type', 'severity', 'camera', 'object_type')
    search_fields = ('event_id', 'details')
