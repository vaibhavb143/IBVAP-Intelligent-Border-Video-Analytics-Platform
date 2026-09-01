from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import WatchlistVehicle

@login_required
def watchlist_list(request):
    vehicles = WatchlistVehicle.objects.all()
    search = request.GET.get('q', '').strip()
    risk = request.GET.get('risk', 'ALL')

    if search:
        vehicles = vehicles.filter(plate_number__icontains=search) | vehicles.filter(description__icontains=search)
    if risk != 'ALL':
        vehicles = vehicles.filter(risk_level=risk)

    return render(request, 'watchlist/index.html', {
        'vehicles': vehicles,
        'search': search,
        'selected_risk': risk,
    })

@login_required
@require_POST
def add_vehicle(request):
    plate_number = request.POST.get('plate_number', '').strip().upper()
    vehicle_type = request.POST.get('vehicle_type', 'Car')
    description = request.POST.get('description', '').strip()
    risk_level = request.POST.get('risk_level', 'HIGH')
    reported_sector = request.POST.get('reported_sector', 'Main Gate')

    if not plate_number:
        messages.error(request, "License Plate Number is required.")
        return redirect('watchlist:list')

    if WatchlistVehicle.objects.filter(plate_number=plate_number).exists():
        messages.warning(request, f"Plate {plate_number} is already in the watchlist database.")
        return redirect('watchlist:list')

    WatchlistVehicle.objects.create(
        plate_number=plate_number,
        vehicle_type=vehicle_type,
        description=description or "Flagged during intelligence review.",
        risk_level=risk_level,
        reported_sector=reported_sector,
    )
    messages.success(request, f"Vehicle {plate_number} successfully registered in Watchlist.")
    return redirect('watchlist:list')

@login_required
@require_POST
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(WatchlistVehicle, pk=pk)
    plate = vehicle.plate_number
    vehicle.delete()
    messages.info(request, f"Vehicle {plate} removed from Watchlist.")
    return redirect('watchlist:list')
