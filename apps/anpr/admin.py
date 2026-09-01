from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from .models import ANPRDetection


@admin.register(ANPRDetection)
class ANPRDetectionAdmin(ModelAdmin):
    list_display = (
        'plate_number',
        'camera',
        'vehicle_type',
        'get_confidence_percent',
        'get_match_badge',
        'watchlist_risk',
        'speed_estimate',
        'direction',
        'timestamp',
    )
    list_filter = (
        'is_watchlist_match',
        ('match_status', ChoicesDropdownFilter),
        ('vehicle_type', ChoicesDropdownFilter),
        ('camera', RelatedDropdownFilter),
    )
    search_fields = ('plate_number', 'camera__camera_id', 'camera__name', 'direction')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)

    fieldsets = (
        (
            'Plate Recognition & Vehicle Type',
            {
                'classes': ['tab'],
                'fields': (
                    'plate_number',
                    'camera',
                    ('vehicle_type', 'confidence'),
                ),
            },
        ),
        (
            'Watchlist Intercept Intelligence',
            {
                'classes': ['tab'],
                'fields': (
                    'is_watchlist_match',
                    ('match_status', 'watchlist_risk'),
                ),
            },
        ),
        (
            'Vehicle Vector & Velocity',
            {
                'classes': ['tab'],
                'fields': (
                    ('speed_estimate', 'direction'),
                    'timestamp',
                ),
            },
        ),
    )

    actions = [
        'flag_as_watchlist_hit',
        'clear_detection_flag',
    ]

    @display(
        description='Watchlist Status',
        label={
            'MATCH': 'danger',
            'FLAGGED': 'warning',
            'CLEARED': 'success',
        }
    )
    def get_match_badge(self, obj):
        return obj.match_status

    @display(description='OCR Confidence')
    def get_confidence_percent(self, obj):
        return f"{obj.confidence * 100:.1f}%"

    @action(description='Flag selected detections as Watchlist Intercept')
    def flag_as_watchlist_hit(self, request, queryset):
        updated = queryset.update(
            is_watchlist_match=True,
            match_status='MATCH',
            watchlist_risk='HIGH'
        )
        self.message_user(request, f"{updated} vehicle plate(s) flagged as Watchlist Intercepts.")

    @action(description='Clear and verify selected detections as Normal')
    def clear_detection_flag(self, request, queryset):
        updated = queryset.update(
            is_watchlist_match=False,
            match_status='CLEARED',
            watchlist_risk='NORMAL'
        )
        self.message_user(request, f"{updated} vehicle detection(s) marked as Cleared.")
