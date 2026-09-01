from django.contrib import admin
from .models import SecurityAlert

@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_id', 'title', 'camera', 'severity', 'threat_score', 'status', 'created_at')
    list_filter = ('severity', 'status', 'camera')
    search_fields = ('alert_id', 'title', 'description')
