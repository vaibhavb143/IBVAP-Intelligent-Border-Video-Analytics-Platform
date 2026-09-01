from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import SecurityEvent
from apps.cameras.models import Camera

@login_required
def event_list(request):
    search = request.GET.get('q', '').strip()
    camera_id = request.GET.get('camera', 'ALL')
    event_type = request.GET.get('type', 'ALL')
    severity = request.GET.get('severity', 'ALL')

    events = SecurityEvent.objects.all().select_related('camera')

    if search:
        events = events.filter(event_id__icontains=search) | events.filter(details__icontains=search)
    if camera_id != 'ALL':
        events = events.filter(camera__camera_id=camera_id)
    if event_type != 'ALL':
        events = events.filter(event_type=event_type)
    if severity != 'ALL':
        events = events.filter(severity=severity)

    cameras = Camera.objects.all()

    return render(request, 'events/index.html', {
        'events': events[:50], # top 50 recent
        'cameras': cameras,
        'search': search,
        'selected_camera': camera_id,
        'selected_type': event_type,
        'selected_severity': severity,
    })

@login_required
def event_evidence_api(request, pk):
    event = get_object_or_404(SecurityEvent, pk=pk)
    return JsonResponse({
        'event_id': event.event_id,
        'camera': f"{event.camera.camera_id} ({event.camera.name})",
        'location': event.camera.location,
        'event_type': event.get_event_type_display(),
        'object_type': event.object_type,
        'threat_score': event.threat_score,
        'severity': event.severity,
        'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S IST'),
        'confidence': f"{int(event.confidence * 100)}%",
        'coordinates': event.coordinates,
        'details': event.details or "AI automated threat detection triggered by virtual perimeter breach.",
        'evidence_image': event.evidence_image,
    })
