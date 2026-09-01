from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import WatchlistVehicle, WatchlistPerson

@login_required
def watchlist_list(request):
    tab = request.GET.get('tab', 'persons') # default to persons or vehicles
    search = request.GET.get('q', '').strip()
    risk = request.GET.get('risk', 'ALL')

    vehicles = WatchlistVehicle.objects.all()
    persons = WatchlistPerson.objects.all()

    if search:
        vehicles = vehicles.filter(plate_number__icontains=search) | vehicles.filter(description__icontains=search)
        persons = persons.filter(full_name__icontains=search) | persons.filter(alias__icontains=search) | persons.filter(person_id__icontains=search) | persons.filter(reason_for_flagging__icontains=search)

    if risk != 'ALL':
        vehicles = vehicles.filter(risk_level=risk)
        persons = persons.filter(threat_level=risk)

    return render(request, 'watchlist/index.html', {
        'vehicles': vehicles,
        'persons': persons,
        'active_tab': tab,
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
        return redirect('/watchlist/?tab=vehicles')

    WatchlistVehicle.objects.create(
        plate_number=plate_number,
        vehicle_type=vehicle_type,
        description=description or "Flagged during intelligence review.",
        risk_level=risk_level,
        reported_sector=reported_sector,
    )
    messages.success(request, f"Vehicle {plate_number} successfully registered in Watchlist.")
    return redirect('/watchlist/?tab=vehicles')

@login_required
@require_POST
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(WatchlistVehicle, pk=pk)
    plate = vehicle.plate_number
    vehicle.delete()
    messages.info(request, f"Vehicle {plate} removed from Watchlist.")
    return redirect('/watchlist/?tab=vehicles')

@login_required
@require_POST
def add_person(request):
    person_id = request.POST.get('person_id', '').strip().upper()
    full_name = request.POST.get('full_name', '').strip()
    alias = request.POST.get('alias', '').strip()
    category = request.POST.get('category', 'INFILTRATOR')
    threat_level = request.POST.get('threat_level', 'HIGH')
    last_seen_sector = request.POST.get('last_seen_sector', 'Sector 01 - Forward Post Alpha')
    reason_for_flagging = request.POST.get('reason_for_flagging', '').strip()

    if not person_id or not full_name:
        messages.error(request, "Person ID and Full Name are required.")
        return redirect('/watchlist/?tab=persons')

    if WatchlistPerson.objects.filter(person_id=person_id).exists():
        messages.warning(request, f"Person with ID {person_id} is already in the FRS biometric watchlist.")
        return redirect('/watchlist/?tab=persons')

    WatchlistPerson.objects.create(
        person_id=person_id,
        full_name=full_name,
        alias=alias,
        category=category,
        threat_level=threat_level,
        last_seen_sector=last_seen_sector,
        reason_for_flagging=reason_for_flagging or "Biometric profile registered for automated FRS tracking.",
    )
    messages.success(request, f"Person {full_name} ({person_id}) registered in Biometric FRS Watchlist.")
    return redirect('/watchlist/?tab=persons')

@login_required
@require_POST
def delete_person(request, pk):
    person = get_object_or_404(WatchlistPerson, pk=pk)
    name = person.full_name
    person.delete()
    messages.info(request, f"Person {name} removed from Biometric Watchlist.")
    return redirect('/watchlist/?tab=persons')
