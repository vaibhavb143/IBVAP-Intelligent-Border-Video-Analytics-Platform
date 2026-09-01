from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Camera

@login_required
def camera_list(request):
    cameras = Camera.objects.all().order_by('camera_id')
    return render(request, 'cameras/index.html', {'cameras': cameras})

@login_required
def camera_detail(request, pk):
    camera = get_object_or_404(Camera, pk=pk)
    return render(request, 'cameras/detail.html', {'camera': camera})

@login_required
@require_POST
def add_camera(request):
    camera_id = request.POST.get('camera_id', '').strip().upper()
    name = request.POST.get('name', '').strip()
    location = request.POST.get('location', '').strip()
    source_type = request.POST.get('source_type', 'VIDEO_FILE')
    feed_type = 'LIVE' if source_type == 'WEBCAM' else 'SIMULATION'
    source_url = request.POST.get('source_url', '').strip()

    if not camera_id or not name:
        messages.error(request, "Camera ID and Name are mandatory.")
        return redirect('cameras:list')

    if Camera.objects.filter(camera_id=camera_id).exists():
        messages.error(request, f"Camera with ID '{camera_id}' already registered.")
        return redirect('cameras:list')

    Camera.objects.create(
        camera_id=camera_id,
        name=name,
        location=location or "Sector Unknown",
        source_type=source_type,
        feed_type=feed_type,
        source_url=source_url,
        enable_human_detection=request.POST.get('enable_human_detection') == 'on',
        enable_vehicle_detection=request.POST.get('enable_vehicle_detection') == 'on',
        enable_anpr=request.POST.get('enable_anpr') == 'on',
        enable_intrusion_detection=request.POST.get('enable_intrusion_detection') == 'on',
        enable_night_detection=request.POST.get('enable_night_detection') == 'on',
    )
    messages.success(request, f"Camera {camera_id} integrated successfully.")
    return redirect('cameras:list')

@login_required
@require_POST
def toggle_ai_module(request, pk):
    camera = get_object_or_404(Camera, pk=pk)
    module = request.POST.get('module')
    
    if module == 'human':
        camera.enable_human_detection = not camera.enable_human_detection
    elif module == 'vehicle':
        camera.enable_vehicle_detection = not camera.enable_vehicle_detection
    elif module == 'anpr':
        camera.enable_anpr = not camera.enable_anpr
    elif module == 'intrusion':
        camera.enable_intrusion_detection = not camera.enable_intrusion_detection
    elif module == 'night':
        camera.enable_night_detection = not camera.enable_night_detection
    elif module == 'ai_master':
        camera.is_ai_active = not camera.is_ai_active
    
    camera.save()
    return JsonResponse({'status': 'ok', 'is_active': getattr(camera, f'enable_{module}', camera.is_ai_active)})
