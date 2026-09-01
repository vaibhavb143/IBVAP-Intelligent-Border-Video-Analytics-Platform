from django.contrib import admin
from .models import Camera

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('camera_id', 'name', 'location', 'feed_type', 'source_type', 'status', 'is_ai_active', 'threat_level')
    list_filter = ('feed_type', 'source_type', 'status', 'threat_level', 'is_ai_active')
    search_fields = ('camera_id', 'name', 'location')
