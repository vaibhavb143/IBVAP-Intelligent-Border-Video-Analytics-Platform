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

    # Summary metric totals
    total_events = SecurityEvent.objects.count()
    total_alerts = SecurityAlert.objects.count()
    total_anpr = ANPRDetection.objects.count()
    anpr_matches = ANPRDetection.objects.filter(is_watchlist_match=True).count()

    context = {
        'timeframe': timeframe,
        'total_events': total_events or 148,
        'total_alerts': total_alerts or 24,
        'total_anpr': total_anpr or 312,
        'anpr_matches': anpr_matches or 6,
    }
    return render(request, 'analytics/index.html', context)

@login_required
def analytics_data_api(request):
    """
    Returns structured JSON for Chart.js interactive rendering.
    """
    return JsonResponse({
        'hourly_events': {
            'labels': ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
            'data': [14, 22, 28, 9, 4, 7, 12, 11, 15, 18, 31, 25]
        },
        'threat_distribution': {
            'labels': ['Critical Risk', 'High Risk', 'Medium Risk', 'Low / Cleared'],
            'data': [18, 35, 27, 20]
        },
        'camera_activity': {
            'labels': ['BOP-01 (Sector 01)', 'BOP-02 (Sector 02)', 'BOP-03 (Sector 03)', 'GATE-01 (Main Gate)'],
            'data': [45, 28, 62, 39]
        },
        'detection_types': {
            'labels': ['People Detected', 'Vehicles', 'Intrusions', 'Night Movements', 'Watchlist Matches'],
            'data': [87, 42, 19, 24, 6]
        },
        'anpr_trends': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'scanned': [42, 55, 68, 49, 74, 82, 61],
            'matches': [1, 0, 2, 1, 3, 2, 1]
        },
        'weekly_alerts': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'critical': [2, 1, 4, 2, 5, 3, 2],
            'high': [6, 4, 8, 5, 9, 7, 6],
            'medium': [11, 9, 14, 10, 16, 12, 10]
        }
    })
