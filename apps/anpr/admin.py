from django.contrib import admin
from .models import ANPRDetection

@admin.register(ANPRDetection)
class ANPRDetectionAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'camera', 'vehicle_type', 'confidence', 'is_watchlist_match', 'match_status', 'timestamp')
    list_filter = ('is_watchlist_match', 'vehicle_type', 'camera')
    search_fields = ('plate_number',)
