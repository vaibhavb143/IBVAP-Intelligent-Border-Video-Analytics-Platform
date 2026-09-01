from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from .models import WatchlistVehicle, WatchlistPerson


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


@admin.register(WatchlistPerson)
class WatchlistPersonAdmin(ModelAdmin):
    list_display = (
        'person_id',
        'full_name',
        'alias',
        'category',
        'get_threat_badge',
        'get_status_badge',
        'last_seen_sector',
        'created_at',
    )
    list_filter = (
        ('threat_level', ChoicesDropdownFilter),
        ('status', ChoicesDropdownFilter),
        ('category', ChoicesDropdownFilter),
    )
    search_fields = ('person_id', 'full_name', 'alias', 'reason_for_flagging', 'last_seen_sector')
    ordering = ('-threat_level', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (
            'Biometric Identity & Classification',
            {
                'classes': ['tab'],
                'fields': (
                    'person_id',
                    ('full_name', 'alias'),
                    ('category', 'threat_level'),
                    'status',
                ),
            },
        ),
        (
            'Facial Recognition & Intelligence Dossier',
            {
                'classes': ['tab'],
                'fields': (
                    'facial_embedding_id',
                    'last_seen_sector',
                    'reason_for_flagging',
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
        'mark_person_apprehended',
        'mark_person_investigating',
        'mark_person_cleared',
        'mark_person_active',
    ]

    @display(
        description='Threat Level',
        label={
            'CRITICAL': 'danger',
            'HIGH': 'warning',
            'MEDIUM': 'info',
            'LOW': 'success',
        }
    )
    def get_threat_badge(self, obj):
        return obj.threat_level

    @display(
        description='FRS Status',
        label={
            'Active': 'danger',
            'Apprehended': 'success',
            'Investigating': 'warning',
            'Cleared': 'info',
        }
    )
    def get_status_badge(self, obj):
        return obj.status

    @action(description='Mark as Apprehended / Detained')
    def mark_person_apprehended(self, request, queryset):
        updated = queryset.update(status='Apprehended')
        self.message_user(request, f"{updated} person(s) marked as Apprehended / Detained.")

    @action(description='Mark as Under Investigation')
    def mark_person_investigating(self, request, queryset):
        updated = queryset.update(status='Investigating')
        self.message_user(request, f"{updated} person(s) placed under active investigation.")

    @action(description='Mark as Cleared / Inactive')
    def mark_person_cleared(self, request, queryset):
        updated = queryset.update(status='Cleared')
        self.message_user(request, f"{updated} person(s) marked as Cleared.")

    @action(description='Mark as Active Wanted Target')
    def mark_person_active(self, request, queryset):
        updated = queryset.update(status='Active')
        self.message_user(request, f"{updated} person(s) set to Active Wanted Notice.")
