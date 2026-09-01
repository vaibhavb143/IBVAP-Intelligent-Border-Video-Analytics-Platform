from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemConfiguration

@login_required
def settings_index(request):
    config = SystemConfiguration.get_settings()
    
    if request.method == 'POST':
        config.night_start_time = request.POST.get('night_start_time', '22:00')
        config.night_end_time = request.POST.get('night_end_time', '05:00')
        config.weight_person_detection = int(request.POST.get('weight_person_detection', 20))
        config.weight_night_movement = int(request.POST.get('weight_night_movement', 15))
        config.weight_restricted_zone = int(request.POST.get('weight_restricted_zone', 30))
        config.weight_loitering = int(request.POST.get('weight_loitering', 10))
        config.weight_watchlist_vehicle = int(request.POST.get('weight_watchlist_vehicle', 40))
        config.auto_refresh_rate = int(request.POST.get('auto_refresh_rate', 5))
        config.audio_alerts = request.POST.get('audio_alerts') == 'on'
        config.save()
        messages.success(request, "Command Center configuration updated successfully.")
        return redirect('settings_app:index')

    return render(request, 'settings_app/index.html', {'config': config})
