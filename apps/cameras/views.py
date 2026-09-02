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
        enable_frs=request.POST.get('enable_frs') == 'on',
        enable_intrusion_detection=request.POST.get('enable_intrusion_detection') == 'on',
        enable_behavioral_analytics=request.POST.get('enable_behavioral_analytics') == 'on',
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
    elif module == 'frs':
        camera.enable_frs = not camera.enable_frs
    elif module == 'intrusion':
        camera.enable_intrusion_detection = not camera.enable_intrusion_detection
    elif module == 'behavioral':
        camera.enable_behavioral_analytics = not camera.enable_behavioral_analytics
    elif module == 'night':
        camera.enable_night_detection = not camera.enable_night_detection
    elif module == 'ai_master':
        camera.is_ai_active = not camera.is_ai_active
    
    camera.save()
    return JsonResponse({'status': 'ok', 'is_active': getattr(camera, f'enable_{module}', camera.is_ai_active)})

@login_required
@require_POST
def analyze_media_api(request):
    from .ai_analyzer import analyze_uploaded_media
    
    file_obj = request.FILES.get('media_file')
    camera_id = request.POST.get('camera_id', 'BOP-01')
    manual_type = request.POST.get('detection_type') # 'auto', 'vehicle', 'person'

    if not file_obj:
        return JsonResponse({'status': 'error', 'message': 'No video or image file provided.'}, status=400)

    result = analyze_uploaded_media(file_obj, camera_id=camera_id, manual_type=manual_type)
    return JsonResponse(result)


# Persistent in-memory trackers & alert throttles per live camera feed
_CAMERA_TRACKERS = {}
_CAMERA_RULES = {}
_CAMERA_LAST_ALERT_TIME = {}

@login_required
@require_POST
def live_frame_inference_api(request):
    """
    Receives real live video frames (base64 encoded) from the operator's webcam or CCTV loop,
    runs actual YOLO detection + object tracking + virtual fence rules in real time,
    and logs genuine security events if an intrusion occurs.
    """
    import base64
    import io
    import time
    from PIL import Image
    from django.utils import timezone
    from .ai.yolo_detector import get_yolo_detector
    from .ai.tracker import RealObjectTracker
    from .ai.rules_engine import SecurityRulesEngine, analyze_frame_luminance
    from .ai.risk_scorer import RiskScorer
    from .ai.evidence_saver import save_evidence_frame
    from apps.alerts.models import SecurityAlert
    from apps.events.models import SecurityEvent

    camera_id = request.POST.get('camera_id', 'BOP-01')
    image_b64 = request.POST.get('image_data', '')

    if not image_b64:
        return JsonResponse({'status': 'error', 'message': 'Missing image frame data.'}, status=400)

    # Strip data URL prefix if present
    if ',' in image_b64:
        image_b64 = image_b64.split(',', 1)[1]

    try:
        image_bytes = base64.b64decode(image_b64)
        frame_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid image frame: {str(e)}'}, status=400)

    # Get singletons / persistent trackers for this camera
    detector = get_yolo_detector()
    if camera_id not in _CAMERA_TRACKERS:
        _CAMERA_TRACKERS[camera_id] = RealObjectTracker(max_disappeared=10, iou_threshold=0.25)
        _CAMERA_RULES[camera_id] = SecurityRulesEngine(loitering_threshold=15.0)

    tracker = _CAMERA_TRACKERS[camera_id]
    rules_engine = _CAMERA_RULES[camera_id]

    if request.POST.get('reset') == '1':
        tracker.reset()

    camera = Camera.objects.filter(camera_id=camera_id).first()

    # 1. Real YOLO Object Detection on Live Frame
    detections = detector.detect(frame_pil, conf_threshold=0.35)

    # 2. Real Tracking
    active_tracks = tracker.update(detections)

    # 3. Real Rule Evaluation
    events = rules_engine.evaluate_rules(
        tracks=active_tracks,
        frame_pil=frame_pil,
        camera=camera
    )

    mean_lum, is_night = analyze_frame_luminance(frame_pil)

    # Build active detections with track IDs for frontend overlay
    tracked_detections = []
    people_count = 0
    vehicle_count = 0

    for track in active_tracks:
        if track.is_person:
            people_count += 1
        elif track.is_vehicle:
            vehicle_count += 1

        tracked_detections.append({
            'track_id': track.track_id,
            'class_name': track.class_name,
            'confidence': round(track.confidence, 2),
            'box': track.box,
            'center': track.center,
            'is_person': track.is_person,
            'is_vehicle': track.is_vehicle,
            'in_restricted_zone': track.in_restricted_zone,
            'trajectory': track.trajectory_direction,
            'dwell_seconds': round(track.zone_duration_seconds, 1)
        })

    now_ts = time.time()
    last_alert_ts = _CAMERA_LAST_ALERT_TIME.get(camera_id, 0)
    cooldown_period = 10.0  # 10s cooldown per camera to avoid spam

    new_alerts = []
    for event in events:
        track_id = event['track_id']
        obj_type = event['object_type']
        event_type = event['event_type']
        conf = event['confidence']

        # Handle ANPR License Plate Extraction for Vehicles
        watchlist_hit = False
        if event_type == 'VEHICLE_DETECTED' or obj_type == 'Vehicle':
            from apps.anpr.models import ANPRDetection
            from apps.watchlist.models import WatchlistVehicle
            from .ai.rules_engine import extract_real_anpr_text, map_vehicle_type

            try:
                bx1, by1, bx2, by2 = [int(v) for v in event.get('bbox', [0, 0, frame_pil.width, frame_pil.height])]
                bx1 = max(0, min(bx1, frame_pil.width - 1))
                by1 = max(0, min(by1, frame_pil.height - 1))
                bx2 = max(bx1 + 1, min(bx2, frame_pil.width))
                by2 = max(by1 + 1, min(by2, frame_pil.height))
                v_crop = frame_pil.crop((bx1, by1, bx2, by2))
                raw_class = event.get('factors', ['Car'])[0].replace('Vehicle Class: ', '')
                ocr_plate, ocr_conf = extract_real_anpr_text(v_crop, track_id=track_id, class_name=raw_class)
            except Exception:
                raw_class = 'car'
                ocr_plate, ocr_conf = extract_real_anpr_text(None, track_id=track_id, class_name=raw_class)

            plate_text = ocr_plate
            match_status = 'CLEARED'
            watchlist_risk = 'NORMAL'

            matched_veh = WatchlistVehicle.objects.filter(plate_number__iexact=plate_text).first()
            if matched_veh:
                watchlist_hit = True
                watchlist_risk = matched_veh.risk_level
                match_status = 'MATCH'
                event_type = 'ANPR_MATCH'
                event['details'] = f"WATCHLIST VEHICLE INTERCEPT: {plate_text} flagged ({watchlist_risk} Risk) at {camera_id}."

            if camera:
                v_class_mapped = map_vehicle_type(raw_class, event.get('bbox'))

                ANPRDetection.objects.create(
                    camera=camera,
                    plate_number=plate_text,
                    vehicle_type=v_class_mapped,
                    confidence=ocr_conf,
                    is_watchlist_match=watchlist_hit,
                    match_status=match_status,
                    watchlist_risk=watchlist_risk,
                    speed_estimate="46 km/h",
                    direction=f"Sector Route ({camera.camera_id})"
                )

        risk_meta = RiskScorer.calculate_risk(
            event_type=event_type,
            object_type=obj_type,
            is_night=is_night,
            is_restricted=('INTRUSION' in event_type or 'FENCE' in event_type),
            is_loitering=('LOITERING' in event_type),
            is_multi=('MULTIPLE' in event_type),
            watchlist_match=watchlist_hit
        )

        threat_score = risk_meta['threat_score']
        severity = risk_meta['severity']

        # Only generate a formal SecurityAlert for genuine security threats (Threat score >= 30 or boundary breaches)
        is_threat = (threat_score >= 30) or ('INTRUSION' in event_type) or ('LOITERING' in event_type) or ('NIGHT' in event_type) or watchlist_hit
        if not is_threat:
            continue

        # Check camera cooldown
        if (now_ts - last_alert_ts) < cooldown_period:
            continue

        _CAMERA_LAST_ALERT_TIME[camera_id] = now_ts

        import uuid
        unique_suffix = uuid.uuid4().hex[:6].upper()
        evt_id = f"EVT-LIVE-{int(time.time()*1000)%10000000}-{unique_suffix}"
        alt_id = f"ALT-LIVE-{int(time.time()*1000)%10000000}-{unique_suffix}"

        evidence_url = save_evidence_frame(
            frame_pil=frame_pil,
            detections=detections,
            event_info={'event_id': evt_id, 'severity': severity},
            camera_id=camera_id
        )

        if camera:
            SecurityEvent.objects.create(
                event_id=evt_id,
                camera=camera,
                event_type=event_type if event_type in dict(SecurityEvent.EVENT_TYPES) else 'INTRUSION',
                object_type=obj_type,
                threat_score=threat_score,
                severity=severity,
                evidence_image=evidence_url,
                details=event['details'],
                confidence=conf,
                coordinates=f"{camera.latitude:.4f} N, {camera.longitude:.4f} E",
                timestamp=timezone.now()
            )

            SecurityAlert.objects.create(
                alert_id=alt_id,
                title=f"{event_type.replace('_', ' ').title()} @ {camera.camera_id}",
                camera=camera,
                severity=severity,
                threat_score=threat_score,
                status='ACTIVE',
                detected_object=obj_type,
                description=f"{event['details']} ({risk_meta['reason']})",
                evidence_image=evidence_url
            )

        new_alerts.append({
            'alert_id': alt_id,
            'title': f"{event_type.replace('_', ' ').title()}",
            'severity': severity,
            'threat_score': threat_score,
            'details': event['details'],
            'evidence_image': evidence_url
        })

    # Update camera live counters
    if camera:
        camera.people_count = people_count
        camera.vehicle_count = vehicle_count
        if len(new_alerts) > 0:
            camera.threat_level = new_alerts[0]['severity']
        elif people_count > 0 or vehicle_count > 0:
            camera.threat_level = 'ELEVATED'
        else:
            camera.threat_level = 'NORMAL'
        camera.status = 'ONLINE'
        camera.save()

    return JsonResponse({
        'status': 'ok',
        'camera_id': camera_id,
        'detections': tracked_detections,
        'new_alerts': new_alerts,
        'people_count': people_count,
        'vehicle_count': vehicle_count,
        'threat_level': camera.threat_level if camera else 'NORMAL',
        'is_night': is_night,
        'luminance': mean_lum
    })


