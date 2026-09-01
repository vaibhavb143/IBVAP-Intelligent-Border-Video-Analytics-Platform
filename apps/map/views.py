from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cameras.models import Camera
from apps.alerts.models import SecurityAlert

@login_required
def map_index(request):
    cameras = Camera.objects.all().order_by('camera_id')
    active_alerts = SecurityAlert.objects.filter(status='ACTIVE')
    
    # Border Sectors Metadata
    sectors = [
        {'code': 'SEC-01', 'name': 'Sector 01 (Northern Ridge)', 'risk': 'CRITICAL', 'threat_score': 92, 'cameras': ['BOP-01', 'BOP-03']},
        {'code': 'SEC-02', 'name': 'Sector 02 (Eastern Plains)', 'risk': 'MEDIUM', 'threat_score': 45, 'cameras': ['BOP-02']},
        {'code': 'SEC-03', 'name': 'Sector 03 (Main Checkpost Gate)', 'risk': 'HIGH', 'threat_score': 80, 'cameras': ['GATE-01']},
    ]

    return render(request, 'map/index.html', {
        'cameras': cameras,
        'active_alerts': active_alerts,
        'sectors': sectors,
    })
