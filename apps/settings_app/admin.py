from django.contrib import admin
from .models import SystemConfiguration

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('night_start_time', 'night_end_time', 'high_threat_threshold', 'auto_refresh_rate', 'updated_at')
