from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cameras.models import Camera
from apps.alerts.models import SecurityAlert
from apps.events.models import SecurityEvent
from apps.settings_app.models import SystemConfiguration

@login_required
def dashboard_index(request):
    cameras = Camera.objects.all().order_by('camera_id')[:6]
    active_alerts = SecurityAlert.objects.filter(status='ACTIVE').select_related('camera')[:6]
    recent_events = SecurityEvent.objects.all().select_related('camera')[:6]
    
    # Calculate real aggregate KPI numbers from live state and database
    total_cameras = Camera.objects.filter(status='ONLINE').count()
    if total_cameras == 0 and cameras.exists():
        total_cameras = cameras.count()
        
    active_alerts_count = SecurityAlert.objects.filter(status='ACTIVE').count()
    people_detected = sum(c.people_count for c in cameras)
    vehicles_detected = sum(c.vehicle_count for c in cameras)
    critical_events_count = SecurityEvent.objects.filter(severity='CRITICAL').count()
    
    # Calculate real dynamic threat score from active alerts
    top_alert = active_alerts.first()
    threat_score = top_alert.threat_score if top_alert else (20 if people_detected > 0 else 0)
    
    if threat_score >= 70:
        threat_level = 'CRITICAL'
    elif threat_score >= 50:
        threat_level = 'HIGH'
    elif threat_score >= 30:
        threat_level = 'ELEVATED'
    else:
        threat_level = 'NORMAL'
    
    config = SystemConfiguration.get_settings()

    # Dynamic Threat Factor Weights from Active Configuration
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
            'system_status': 'AI ENGINE ONLINE',
        },
        'threat_score': threat_score,
        'threat_level': threat_level,
        'threat_breakdown': threat_breakdown,
        'config': config,
    }
    return render(request, 'dashboard/index.html', context)

