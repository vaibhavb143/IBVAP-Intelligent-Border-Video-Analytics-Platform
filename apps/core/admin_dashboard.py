"""
IBVAP Admin Dashboard Callback for Django Unfold.
Provides real-time surveillance telemetry, alert metrics, and operational statistics.
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q


def dashboard_callback(request, context):
    """
    Callback function executed by Unfold to enrich the super admin index context.
    """
    try:
        from apps.cameras.models import Camera
        from apps.alerts.models import SecurityAlert
        from apps.events.models import SecurityEvent
        from apps.anpr.models import ANPRDetection
        from apps.watchlist.models import WatchlistVehicle
        from apps.settings_app.models import SystemConfiguration

        # Cameras Telemetry
        total_cameras = Camera.objects.count()
        online_cameras = Camera.objects.filter(status='ONLINE').count()
        ai_active_cameras = Camera.objects.filter(is_ai_active=True).count()
        critical_cameras = Camera.objects.filter(threat_level='CRITICAL').count()

        # Alerts Telemetry
        active_alerts = SecurityAlert.objects.filter(status='ACTIVE').count()
        critical_alerts = SecurityAlert.objects.filter(severity='CRITICAL', status='ACTIVE').count()
        acknowledged_alerts = SecurityAlert.objects.filter(status='ACKNOWLEDGED').count()
        resolved_alerts = SecurityAlert.objects.filter(status='RESOLVED').count()

        # ANPR & Watchlist Telemetry
        total_detections = ANPRDetection.objects.count()
        watchlist_matches = ANPRDetection.objects.filter(is_watchlist_match=True).count()
        active_watchlist = WatchlistVehicle.objects.filter(status='Active').count()
        critical_watchlist = WatchlistVehicle.objects.filter(risk_level='CRITICAL', status='Active').count()

        # Events Telemetry (24h)
        last_24h = timezone.now() - timedelta(hours=24)
        events_24h = SecurityEvent.objects.filter(timestamp__gte=last_24h).count()
        intrusions_24h = SecurityEvent.objects.filter(timestamp__gte=last_24h, event_type='INTRUSION').count()

        # Recent priority lists for dashboard widgets
        recent_critical_alerts = SecurityAlert.objects.filter(
            status__in=['ACTIVE', 'ACKNOWLEDGED']
        ).select_related('camera').order_by('-threat_score', '-created_at')[:5]

        recent_events = SecurityEvent.objects.select_related('camera').order_by('-timestamp')[:5]
        recent_anpr = ANPRDetection.objects.select_related('camera').order_by('-timestamp')[:5]

        config = SystemConfiguration.get_settings()

        # Operational Readiness calculation
        camera_readiness = int((online_cameras / total_cameras * 100)) if total_cameras > 0 else 100
        ai_coverage = int((ai_active_cameras / total_cameras * 100)) if total_cameras > 0 else 100

        kpis = {
            'total_cameras': total_cameras,
            'online_cameras': online_cameras,
            'ai_active_cameras': ai_active_cameras,
            'critical_cameras': critical_cameras,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'acknowledged_alerts': acknowledged_alerts,
            'resolved_alerts': resolved_alerts,
            'total_detections': total_detections,
            'watchlist_matches': watchlist_matches,
            'active_watchlist': active_watchlist,
            'critical_watchlist': critical_watchlist,
            'events_24h': events_24h,
            'intrusions_24h': intrusions_24h,
            'camera_readiness': camera_readiness,
            'ai_coverage': ai_coverage,
            'recent_critical_alerts': recent_critical_alerts,
            'recent_events': recent_events,
            'recent_anpr': recent_anpr,
            'system_config': config,
        }

        context['ibvap_kpis'] = kpis

    except Exception as e:
        context['ibvap_kpi_error'] = str(e)

    return context
