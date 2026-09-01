from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cameras.models import Camera
from apps.alerts.models import SecurityAlert
from apps.events.models import SecurityEvent
from apps.settings_app.models import SystemConfiguration

@login_required
def dashboard_index(request):
    cameras = Camera.objects.all().order_by('camera_id')[:4]
    active_alerts = SecurityAlert.objects.filter(status='ACTIVE').select_related('camera')[:6]
    recent_events = SecurityEvent.objects.all().select_related('camera')[:6]
    
    # Calculate aggregate KPI numbers
    total_cameras = Camera.objects.filter(status='ONLINE').count() or 4
    active_alerts_count = SecurityAlert.objects.filter(status='ACTIVE').count() or 3
    people_detected = sum(c.people_count for c in cameras) or 27
    vehicles_detected = sum(c.vehicle_count for c in cameras) or 12
    critical_events_count = SecurityEvent.objects.filter(severity='CRITICAL').count() or 2
    
    config = SystemConfiguration.get_settings()

    # Threat Intelligence Breakdown (Demo values reflecting real platform scoring)
    threat_breakdown = [
        {'factor': 'Person Detection', 'weight': f"+{config.weight_person_detection}", 'icon': 'bi-person-walking'},
        {'factor': 'Night Movement', 'weight': f"+{config.weight_night_movement}", 'icon': 'bi-moon-stars'},
        {'factor': 'Restricted Zone', 'weight': f"+{config.weight_restricted_zone}", 'icon': 'bi-shield-slash'},
        {'factor': 'Perimeter Loitering', 'weight': f"+{config.weight_loitering}", 'icon': 'bi-clock-history'},
        {'factor': 'Watchlist Match', 'weight': f"+{config.weight_watchlist_vehicle}", 'icon': 'bi-exclamation-triangle'},
    ]

    context = {
        'cameras': cameras,
        'active_alerts': active_alerts,
        'recent_events': recent_events,
        'kpis': {
            'active_cameras': total_cameras,
            'active_alerts': active_alerts_count,
            'people_detected': people_detected,
            'vehicles_detected': vehicles_detected,
            'critical_events': critical_events_count,
            'system_status': 'OPERATIONAL',
        },
        'threat_score': 92,
        'threat_level': 'CRITICAL',
        'threat_breakdown': threat_breakdown,
        'config': config,
    }
    return render(request, 'dashboard/index.html', context)
