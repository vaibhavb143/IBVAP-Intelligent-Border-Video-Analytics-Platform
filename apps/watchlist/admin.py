from django.contrib import admin
from .models import WatchlistVehicle

@admin.register(WatchlistVehicle)
class WatchlistVehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'vehicle_type', 'risk_level', 'status', 'reported_sector', 'created_at')
    list_filter = ('risk_level', 'status', 'vehicle_type')
    search_fields = ('plate_number', 'description')
