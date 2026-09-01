from django.utils import timezone

def global_system_context(request):
    """
    Supplies global command-center state to all templates.
    """
    unread_alerts_count = 0
    active_threat_level = 92
    
    try:
        from apps.alerts.models import SecurityAlert
        unread_alerts_count = SecurityAlert.objects.filter(status='ACTIVE').count()
        recent_notifications = SecurityAlert.objects.filter(status='ACTIVE').order_by('-created_at')[:5]
    except Exception:
        recent_notifications = []

    return {
        'SYSTEM_NAME': 'IBVAP',
        'SYSTEM_FULL_NAME': 'Intelligent Border Video Analytics Platform',
        'SYSTEM_TAGLINE': 'Transforming Existing CCTV into Intelligent Border Security',
        'SYSTEM_STATUS': 'OPERATIONAL',
        'UNREAD_ALERTS_COUNT': unread_alerts_count,
        'RECENT_NOTIFICATIONS': recent_notifications,
        'CURRENT_TIMESTAMP': timezone.now(),
    }
