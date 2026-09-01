from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from .models import WatchlistVehicle


@admin.register(WatchlistVehicle)
class WatchlistVehicleAdmin(ModelAdmin):
    list_display = (
        'plate_number',
        'vehicle_type',
        'get_risk_badge',
        'get_status_badge',
        'reported_sector',
        'created_at',
    )
    list_filter = (
        ('risk_level', ChoicesDropdownFilter),
        ('status', ChoicesDropdownFilter),
    )
    search_fields = ('plate_number', 'description', 'reported_sector')
    ordering = ('-risk_level', '-created_at')
    readonly_fields = ('created_at',)

    fieldsets = (
        (
            'Target Vehicle Identification',
            {
                'classes': ['tab'],
                'fields': (
                    'plate_number',
                    'vehicle_type',
                    'reported_sector',
                ),
            },
        ),
        (
            'Threat Assessment & Intercept Directives',
            {
                'classes': ['tab'],
                'fields': (
                    ('risk_level', 'status'),
                    'description',
                ),
            },
        ),
        (
            'Watchlist Audit Timestamp',
            {
                'classes': ['tab'],
                'fields': (
                    'created_at',
                ),
            },
        ),
    )

    actions = [
        'mark_under_investigation',
        'mark_resolved_cleared',
        'mark_active_threat',
    ]

    @display(
        description='Risk Priority',
        label={
            'CRITICAL': 'danger',
            'HIGH': 'warning',
            'MEDIUM': 'info',
            'LOW': 'success',
        }
    )
    def get_risk_badge(self, obj):
        return obj.risk_level

    @display(
        description='Investigation Status',
        label={
            'Active': 'danger',
            'Investigating': 'warning',
            'Resolved': 'success',
        }
    )
    def get_status_badge(self, obj):
        return obj.status

    @action(description='Set status: Under Active Investigation')
    def mark_under_investigation(self, request, queryset):
        updated = queryset.update(status='Investigating')
        self.message_user(request, f"{updated} vehicle(s) placed under active investigation.")

    @action(description='Set status: Resolved / Cleared')
    def mark_resolved_cleared(self, request, queryset):
        updated = queryset.update(status='Resolved')
        self.message_user(request, f"{updated} vehicle(s) marked as resolved / cleared.")

    @action(description='Set status: Active High-Priority Flag')
    def mark_active_threat(self, request, queryset):
        updated = queryset.update(status='Active')
        self.message_user(request, f"{updated} vehicle(s) set to active flag.")
