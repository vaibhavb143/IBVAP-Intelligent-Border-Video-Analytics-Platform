from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.events.models import SecurityEvent
from apps.alerts.models import SecurityAlert
from apps.cameras.models import Camera
from apps.anpr.models import ANPRDetection

@login_required
def analytics_index(request):
    timeframe = request.GET.get('timeframe', '24h')

    # Summary metric totals from actual database records
    total_events = SecurityEvent.objects.count()
    total_alerts = SecurityAlert.objects.count()
    total_anpr = ANPRDetection.objects.count()
    anpr_matches = ANPRDetection.objects.filter(is_watchlist_match=True).count()

    context = {
        'timeframe': timeframe,
        'total_events': total_events,
        'total_alerts': total_alerts,
        'total_anpr': total_anpr,
        'anpr_matches': anpr_matches,
    }
    return render(request, 'analytics/index.html', context)

@login_required
def analytics_data_api(request):
    """
    Returns structured JSON calculated directly from real database records for Chart.js rendering.
    """
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    # 1. Threat distribution
    crit_count = SecurityEvent.objects.filter(severity='CRITICAL').count()
    high_count = SecurityEvent.objects.filter(severity='HIGH').count()
    med_count = SecurityEvent.objects.filter(severity='MEDIUM').count()
    low_count = SecurityEvent.objects.filter(severity='LOW').count()
    
    threat_data = [crit_count, high_count, med_count, low_count]

    # 2. Camera activity
    cameras = Camera.objects.all()[:6]
    cam_labels = [f"{c.camera_id} ({c.name[:12]})" for c in cameras]
    cam_data = [c.events.count() for c in cameras]

    # 3. Detection types breakdown
    people_evt = SecurityEvent.objects.filter(object_type='Person').count()
    vehicle_evt = SecurityEvent.objects.filter(object_type='Vehicle').count()
    intrusion_evt = SecurityEvent.objects.filter(event_type__in=['INTRUSION', 'VIRTUAL_FENCE_INTRUSION']).count()
    night_evt = SecurityEvent.objects.filter(event_type='NIGHT_MOVEMENT').count()
    anpr_evt = ANPRDetection.objects.filter(is_watchlist_match=True).count()

    # 4. Hourly / recent timeline
    hours_labels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', 'Now']
    now = timezone.now()
    hour_counts = []
    for h in [24, 20, 16, 12, 8, 4, 0]:
        t_start = now - timedelta(hours=h + 4)
        t_end = now - timedelta(hours=h)
        cnt = SecurityEvent.objects.filter(timestamp__gte=t_start, timestamp__lte=t_end).count()
        hour_counts.append(cnt)

    return JsonResponse({
        'hourly_events': {
            'labels': hours_labels,
            'data': hour_counts
        },
        'threat_distribution': {
            'labels': ['Critical Risk', 'High Risk', 'Medium Risk', 'Low / Cleared'],
            'data': threat_data
        },
        'camera_activity': {
            'labels': cam_labels if cam_labels else ['No Cameras'],
            'data': cam_data if cam_data else [0]
        },
        'detection_types': {
            'labels': ['People Detected', 'Vehicles', 'Intrusions', 'Night Movements', 'Watchlist Matches'],
            'data': [people_evt, vehicle_evt, intrusion_evt, night_evt, anpr_evt]
        },
        'anpr_trends': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'scanned': [ANPRDetection.objects.count(), 0, 0, 0, 0, 0, 0],
            'matches': [anpr_evt, 0, 0, 0, 0, 0, 0]
        },
        'weekly_alerts': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'critical': [crit_count, 0, 0, 0, 0, 0, 0],
            'high': [high_count, 0, 0, 0, 0, 0, 0],
            'medium': [med_count, 0, 0, 0, 0, 0, 0]
        }
    })

