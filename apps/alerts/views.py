from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import SecurityAlert
from apps.cameras.models import Camera

@login_required
def alert_list(request):
    severity_filter = request.GET.get('severity', 'ALL')
    camera_filter = request.GET.get('camera', 'ALL')
    status_filter = request.GET.get('status', 'ALL')

    alerts = SecurityAlert.objects.all().select_related('camera', 'acknowledged_by')

    if severity_filter != 'ALL':
        alerts = alerts.filter(severity=severity_filter)
    if camera_filter != 'ALL':
        alerts = alerts.filter(camera__camera_id=camera_filter)
    if status_filter != 'ALL':
        alerts = alerts.filter(status=status_filter)

    counts = {
        'all': SecurityAlert.objects.count(),
        'critical': SecurityAlert.objects.filter(severity='CRITICAL').count(),
        'high': SecurityAlert.objects.filter(severity='HIGH').count(),
        'medium': SecurityAlert.objects.filter(severity='MEDIUM').count(),
        'low': SecurityAlert.objects.filter(severity='LOW').count(),
        'resolved': SecurityAlert.objects.filter(status='RESOLVED').count(),
        'active': SecurityAlert.objects.filter(status='ACTIVE').count(),
    }

    cameras = Camera.objects.all()

    return render(request, 'alerts/index.html', {
        'alerts': alerts,
        'counts': counts,
        'cameras': cameras,
        'selected_severity': severity_filter,
        'selected_camera': camera_filter,
        'selected_status': status_filter,
    })

@login_required
@require_POST
def acknowledge_alert(request, pk):
    alert = get_object_or_404(SecurityAlert, pk=pk)
    alert.status = 'ACKNOWLEDGED'
    alert.acknowledged_by = request.user
    alert.acknowledged_at = timezone.now()
    alert.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'new_status': 'ACKNOWLEDGED'})
    messages.success(request, f"Alert {alert.alert_id} acknowledged.")
    return redirect('alerts:list')

@login_required
@require_POST
def resolve_alert(request, pk):
    alert = get_object_or_404(SecurityAlert, pk=pk)
    alert.status = 'RESOLVED'
    alert.resolved_at = timezone.now()
    alert.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'new_status': 'RESOLVED'})
    messages.success(request, f"Alert {alert.alert_id} resolved and cleared.")
    return redirect('alerts:list')

@login_required
@require_POST
def delete_alert(request, pk):
    alert = get_object_or_404(SecurityAlert, pk=pk)
    alert_id = alert.alert_id
    alert.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'deleted_id': alert_id})
    messages.success(request, f"Alert {alert_id} deleted.")
    return redirect('alerts:list')

@login_required
@require_POST
def clear_all_alerts(request):
    """
    Purges all active/resolved alerts and resets camera threat scores.
    """
    deleted_count = SecurityAlert.objects.all().delete()[0]
    Camera.objects.all().update(threat_level='NORMAL', people_count=0, vehicle_count=0)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'deleted_count': deleted_count})
    messages.success(request, f"All {deleted_count} alerts cleared successfully.")
    return redirect('alerts:list')
