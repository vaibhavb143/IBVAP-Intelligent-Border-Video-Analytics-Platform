/**
 * IBVAP SOC Dashboard — Real-Time Edge AI Stream & Telemetry Controller
 * Connects physical webcam & simulated CCTV video feeds to backend neural YOLO detector, tracker, and rules engine.
 * Renders authentic bounding boxes, track IDs, confidence scores, and real-time security alerts.
 */

const ACTIVE_FEEDS = {};

document.addEventListener('DOMContentLoaded', () => {
    // CAM-01: Real Physical Webcam
    initCameraAIStream('BOP-01', true);

    // CAM-02 through CAM-06: Simulated CCTV Streams (Standby until video asset is loaded)
    initSimulatedStandby('BOP-02', 'BOP-02 (Eastern Sector)');
    initSimulatedStandby('BOP-03', 'BOP-03 (Restricted Outpost)');
    initSimulatedStandby('BOP-04', 'BOP-04 (Northern Ridge)');
    initSimulatedStandby('BOP-05', 'BOP-05 (Riverine Basin)');
    initSimulatedStandby('GATE-01', 'GATE-01 (Checkpost Sector)');
});

/**
 * Purge all Security Alerts via AJAX API
 */
async function clearAllSecurityAlerts() {
    if (!confirm("Are you sure you want to clear and purge all active security alerts from the system?")) return;
    try {
        const response = await fetch('/alerts/clear-all/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') || '',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        const data = await response.json();
        if (data.status === 'success') {
            const streamContainer = document.querySelector('.alert-stream-list');
            if (streamContainer) {
                streamContainer.innerHTML = '<div class="text-center text-muted small py-4"><i class="bi bi-shield-check text-success me-1"></i> All security alerts cleared. Sector secure.</div>';
            }
            const threatBadge = document.querySelector('.threat-badge-crit');
            if (threatBadge) {
                threatBadge.className = 'badge bg-success font-monospace text-xs';
                threatBadge.textContent = 'NORMAL';
            }
            const threatNum = document.querySelector('.threat-num');
            if (threatNum) threatNum.textContent = '0';

            const kpiAlerts = document.querySelectorAll('.kpi-value');
            if (kpiAlerts.length >= 2) kpiAlerts[1].textContent = '0';
        }
    } catch (err) {
        console.error("Error clearing alerts:", err);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Universal Camera AI Stream Controller (Handles physical Webcam or CCTV Video File)
 */
function initCameraAIStream(cameraId, isWebcam = false) {
    const videoEl = document.getElementById(`video-${cameraId}`);
    const canvasEl = document.getElementById(`canvas-${cameraId}`);
    const toggleBtn = document.getElementById(`btn-webcam-${cameraId}`);
    
    if (!canvasEl || !videoEl) return;
    const ctx = canvasEl.getContext('2d');
    canvasEl.width = 640;
    canvasEl.height = 360;

    // Destroy existing feed instance if running
    if (ACTIVE_FEEDS[cameraId]) {
        ACTIVE_FEEDS[cameraId].stop();
    }

    const feedState = {
        cameraId: cameraId,
        isWebcam: isWebcam,
        stream: null,
        inferenceInterval: null,
        animFrameId: null,
        isProcessingFrame: false,
        latestDetections: [],
        isNightCondition: false,
        currentLuminance: 120.0,
        needsReset: true,
        running: true
    };

    const offCanvas = document.createElement('canvas');
    offCanvas.width = 640;
    offCanvas.height = 360;
    const offCtx = offCanvas.getContext('2d');

    async function start() {
        feedState.needsReset = true;
        if (isWebcam) {
            try {
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    feedState.stream = await navigator.mediaDevices.getUserMedia({
                        video: { width: { ideal: 640 }, height: { ideal: 360 }, frameRate: { ideal: 30 } },
                        audio: false
                    });

                    videoEl.srcObject = feedState.stream;
                    videoEl.style.display = 'none';
                    await videoEl.play();

                    if (toggleBtn) {
                        toggleBtn.innerHTML = '<i class="bi bi-camera-video-off"></i> Stop Webcam';
                        toggleBtn.classList.remove('btn-soc-primary');
                        toggleBtn.classList.add('btn-soc-secondary');
                    }
                }
            } catch (err) {
                console.warn(`[IBVAP] Webcam error on ${cameraId}:`, err);
                initSimulatedStandby(cameraId, `${cameraId} (Disconnected)`);
                return;
            }
        } else {
            // Video element playing source
            videoEl.style.display = 'none';
            await videoEl.play();
        }

        // Display loop
        render();

        // Backend AI Inference loop (~2.5 inferences/second)
        feedState.inferenceInterval = setInterval(sendFrameForInference, 400);
    }

    function stop() {
        feedState.running = false;
        if (feedState.stream) {
            feedState.stream.getTracks().forEach(t => t.stop());
            feedState.stream = null;
        }
        if (feedState.inferenceInterval) {
            clearInterval(feedState.inferenceInterval);
            feedState.inferenceInterval = null;
        }
        if (feedState.animFrameId) {
            cancelAnimationFrame(feedState.animFrameId);
            feedState.animFrameId = null;
        }
        if (toggleBtn && isWebcam) {
            toggleBtn.innerHTML = '<i class="bi bi-camera-video"></i> Start Webcam';
            toggleBtn.classList.remove('btn-soc-secondary');
            toggleBtn.classList.add('btn-soc-primary');
        }
        videoEl.pause();
        feedState.latestDetections = [];
    }

    async function sendFrameForInference() {
        if (!feedState.running || !videoEl || videoEl.readyState < 2 || feedState.isProcessingFrame) return;

        feedState.isProcessingFrame = true;
        try {
            offCtx.drawImage(videoEl, 0, 0, offCanvas.width, offCanvas.height);
            const dataUrl = offCanvas.toDataURL('image/jpeg', 0.65);

            const formData = new FormData();
            formData.append('camera_id', cameraId);
            formData.append('image_data', dataUrl);
            if (feedState.needsReset) {
                formData.append('reset', '1');
                feedState.needsReset = false;
            }

            const response = await fetch('/cameras/live-inference/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.status === 'ok') {
                    feedState.latestDetections = data.detections || [];
                    feedState.isNightCondition = data.is_night;
                    feedState.currentLuminance = data.luminance;

                    updateLiveTelemetry(cameraId, data);

                    if (data.new_alerts && data.new_alerts.length > 0) {
                        data.new_alerts.forEach(alert => prependLiveAlert(alert, cameraId));
                    }
                }
            }
        } catch (err) {
            console.error(`[IBVAP] Live inference error on ${cameraId}:`, err);
        } finally {
            feedState.isProcessingFrame = false;
        }
    }

    function render() {
        if (!feedState.running) return;

        if (videoEl && videoEl.readyState >= 2) {
            // 1. Draw actual video frame
            ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);

            // 2. Vertical Restricted Boundary Line & Protected Zone (Only on Real Webcam Demo: isWebcam)
            let lineX = Math.round(canvasEl.width * 0.75);
            let isBreached = false;

            if (isWebcam) {
                isBreached = feedState.latestDetections.some(det => 
                    det.in_restricted_zone || (det.is_person && ((det.box && det.box[2] > lineX) || (det.center && det.center[0] > lineX)))
                );

                // Shaded Restricted Right Zone
                ctx.fillStyle = isBreached ? 'rgba(244, 63, 94, 0.25)' : 'rgba(244, 63, 94, 0.09)';
                ctx.fillRect(lineX, 22, canvasEl.width - lineX, canvasEl.height - 22);

                // Vertical Laser Line Glow
                ctx.save();
                ctx.shadowColor = isBreached ? '#ff1744' : '#f43f5e';
                ctx.shadowBlur = isBreached ? 12 : 6;
                ctx.strokeStyle = isBreached ? '#ff1744' : '#f43f5e';
                ctx.lineWidth = isBreached ? 3.0 : 2.0;
                ctx.setLineDash([10, 5]);
                ctx.beginPath();
                ctx.moveTo(lineX, 22);
                ctx.lineTo(lineX, canvasEl.height);
                ctx.stroke();
                ctx.setLineDash([]);

                // Vertical line emitter nodes (Top & Bottom markers)
                ctx.fillStyle = isBreached ? '#ff1744' : '#00f2fe';
                ctx.beginPath(); ctx.arc(lineX, 26, 4, 0, Math.PI * 2); ctx.fill();
                ctx.beginPath(); ctx.arc(lineX, canvasEl.height - 6, 4, 0, Math.PI * 2); ctx.fill();
                ctx.restore();

                // Boundary Label & Tactical HUD Indicators
                ctx.save();
                if (isBreached) {
                    // Flashing breach warning badge
                    ctx.fillStyle = '#ff1744';
                    ctx.fillRect(lineX - 180, 26, 175, 22);
                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 10px "JetBrains Mono", monospace';
                    ctx.fillText('⚠️ LINE BREACH DETECTED!', lineX - 174, 41);

                    // Warning indicator inside right sector
                    ctx.fillStyle = 'rgba(255, 23, 68, 0.95)';
                    ctx.font = 'bold 10px "JetBrains Mono", monospace';
                    ctx.fillText('⚡ INTRUSION', lineX + 6, 41);
                } else {
                    // Standby Restricted Line Tag
                    ctx.fillStyle = 'rgba(244, 63, 94, 0.95)';
                    ctx.font = 'bold 9px "JetBrains Mono", monospace';
                    ctx.fillText('⚡ RESTRICTED LINE', lineX + 6, 38);
                    ctx.fillStyle = 'rgba(244, 63, 94, 0.70)';
                    ctx.font = '8px "JetBrains Mono", monospace';
                    ctx.fillText('▶ NO-ENTRY ZONE', lineX + 6, 50);
                }

                // Diagonal hazard hatch markings across the vertical border
                ctx.strokeStyle = isBreached ? 'rgba(255, 23, 68, 0.45)' : 'rgba(244, 63, 94, 0.25)';
                ctx.lineWidth = 1;
                for (let hy = 65; hy < canvasEl.height - 15; hy += 25) {
                    ctx.beginPath();
                    ctx.moveTo(lineX, hy);
                    ctx.lineTo(lineX + 16, hy + 16);
                    ctx.stroke();
                }
                ctx.restore();
            }

            // 3. Draw Real YOLO Bounding Boxes & Tracking
            feedState.latestDetections.forEach(det => {
                const [bx1, by1, bx2, by2] = det.box;
                const isIntruder = isWebcam 
                    ? (det.in_restricted_zone || det.dwell_seconds > 0 || (det.is_person && (bx2 > lineX || (det.center && det.center[0] > lineX))))
                    : (det.in_restricted_zone || det.dwell_seconds > 0);
                const strokeColor = isIntruder ? '#ff1744' : (det.is_person ? '#00f2fe' : '#f59e0b');
                const fillColor = isIntruder ? 'rgba(244, 63, 94, 0.25)' : 'rgba(0, 242, 254, 0.10)';

                const w = bx2 - bx1;
                const h = by2 - by1;

                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = isIntruder ? 2.5 : 2;
                ctx.strokeRect(bx1, by1, w, h);
                ctx.fillStyle = fillColor;
                ctx.fillRect(bx1, by1, w, h);

                // Tactical corner brackets
                const cornerLen = Math.min(10, w / 4);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(bx1, by1 + cornerLen); ctx.lineTo(bx1, by1); ctx.lineTo(bx1 + cornerLen, by1);
                ctx.moveTo(bx2, by2 - cornerLen); ctx.lineTo(bx2, by2); ctx.lineTo(bx2 - cornerLen, by2);
                ctx.stroke();

                const label = isIntruder && det.is_person 
                    ? `🚨 INTRUDER #${det.track_id} [${Math.round(det.confidence * 100)}%] // BREACH` 
                    : `${det.class_name.toUpperCase()} #${det.track_id} [${Math.round(det.confidence * 100)}%]`;
                ctx.font = 'bold 11px "JetBrains Mono", monospace';
                const textWidth = ctx.measureText(label).width;

                ctx.fillStyle = strokeColor;
                ctx.fillRect(bx1, Math.max(0, by1 - 18), textWidth + 8, 18);

                ctx.fillStyle = '#ffffff';
                ctx.fillText(label, bx1 + 4, Math.max(12, by1 - 5));

                if (det.trajectory && det.trajectory !== 'STATIONARY') {
                    ctx.fillStyle = isIntruder ? '#ff4081' : '#ffffff';
                    ctx.font = '9px "JetBrains Mono", monospace';
                    ctx.fillText(`DIR: ${det.trajectory}`, bx1, by2 + 12);
                }
            });

            // 4. Tactical HUD Header
            ctx.fillStyle = 'rgba(5, 10, 20, 0.75)';
            ctx.fillRect(0, 0, canvasEl.width, 22);

            ctx.fillStyle = '#00f2fe';
            ctx.font = '10px "JetBrains Mono", monospace';
            const now = new Date();
            const timeStr = now.toTimeString().split(' ')[0] + '.' + Math.floor(now.getMilliseconds() / 100);
            const feedTypeLabel = isWebcam ? 'LIVE WEBCAM' : 'SIMULATED CCTV STREAM';
            ctx.fillText(`${feedTypeLabel} // ${cameraId} | FPS: 30.0 | LUMA: ${Math.round(feedState.currentLuminance)}`, 8, 15);
            ctx.fillText(`${timeStr} IST`, canvasEl.width - 95, 15);
        }

        feedState.animFrameId = requestAnimationFrame(render);
    }

    feedState.stop = stop;
    ACTIVE_FEEDS[cameraId] = feedState;

    if (isWebcam && toggleBtn) {
        toggleBtn.onclick = () => {
            if (feedState.running && feedState.stream) {
                stop();
                initSimulatedStandby(cameraId, `${cameraId} (Standby)`);
            } else {
                initCameraAIStream(cameraId, true);
            }
        };
    }

    start();
}

/**
 * Load User-Provided CCTV Video File into Any Camera Channel
 */
function loadCCTVVideoFile(cameraId, inputElement) {
    if (!inputElement || !inputElement.files || !inputElement.files[0]) return;

    const file = inputElement.files[0];
    const videoEl = document.getElementById(`video-${cameraId}`);
    if (!videoEl) return;

    const objectUrl = URL.createObjectURL(file);
    videoEl.src = objectUrl;
    videoEl.loop = true;
    videoEl.muted = true;

    // Update status badge and replace button with "Stop Video"
    const card = document.getElementById(`card-${cameraId}`);
    if (card) {
        const badge = card.querySelector('.feed-status-badge');
        if (badge) {
            badge.className = 'feed-status-badge badge-simulation text-success';
            badge.innerHTML = '● SIMULATED CCTV STREAM (PLAYING)';
        }
        const btnContainer = card.querySelector('.camera-feed-footer div');
        if (btnContainer) {
            btnContainer.innerHTML = `
                <button type="button" class="btn btn-sm btn-danger py-0 px-2 font-monospace" style="font-size: 0.72rem;" onclick="stopCCTVVideo('${cameraId}')">
                    <i class="bi bi-stop-circle me-1"></i> Stop Video
                </button>
            `;
        }
    }

    // Start AI stream on this camera
    initCameraAIStream(cameraId, false);
}

/**
 * Stop Video Playback & Return Camera Channel to Standby Radar
 */
function stopCCTVVideo(cameraId) {
    const videoEl = document.getElementById(`video-${cameraId}`);
    if (videoEl) {
        videoEl.pause();
        videoEl.removeAttribute('src');
        videoEl.load();
    }

    if (ACTIVE_FEEDS[cameraId]) {
        ACTIVE_FEEDS[cameraId].stop();
        delete ACTIVE_FEEDS[cameraId];
    }

    const card = document.getElementById(`card-${cameraId}`);
    if (card) {
        const badge = card.querySelector('.feed-status-badge');
        if (badge) {
            badge.className = 'feed-status-badge badge-simulation';
            badge.innerHTML = '● SIMULATION — VIDEO';
        }
        const btnContainer = card.querySelector('.camera-feed-footer div');
        if (btnContainer) {
            btnContainer.innerHTML = `
                <input type="file" id="file-${cameraId}" accept="video/*" style="display: none;" onchange="loadCCTVVideoFile('${cameraId}', this)">
                <button type="button" class="btn btn-sm btn-soc-secondary py-0 px-2 font-monospace" style="font-size: 0.72rem;" onclick="document.getElementById('file-${cameraId}').click()" title="Upload surveillance video to run real-time AI inference on this channel">
                    <i class="bi bi-file-earmark-play"></i> Ingest CCTV Video
                </button>
            `;
        }
    }

    initSimulatedStandby(cameraId, `${cameraId} (Standby)`);
}

/**
 * Standby Tactical Radar for Inactive Channels
 */
function initSimulatedStandby(cameraId, label) {
    const canvas = document.getElementById(`canvas-${cameraId}`);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = 640;
    canvas.height = 360;

    let scanY = 0;
    let animId = null;

    if (ACTIVE_FEEDS[cameraId]) {
        ACTIVE_FEEDS[cameraId].stop();
        delete ACTIVE_FEEDS[cameraId];
    }

    function renderStandby() {
        ctx.fillStyle = '#040812';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Grid
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.05)';
        ctx.lineWidth = 1;
        for (let x = 0; x < canvas.width; x += 40) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += 40) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
        }

        // Radar line
        scanY = (scanY + 1.2) % canvas.height;
        ctx.fillStyle = 'rgba(0, 242, 254, 0.06)';
        ctx.fillRect(0, scanY, canvas.width, 3);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;

        ctx.strokeStyle = 'rgba(0, 242, 254, 0.25)';
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(cx, cy, 40, 0, Math.PI * 2); ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(cx - 50, cy); ctx.lineTo(cx + 50, cy);
        ctx.moveTo(cx, cy - 50); ctx.lineTo(cx + 50, cy);
        ctx.stroke();

        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 11px "JetBrains Mono", monospace';
        ctx.textAlign = 'center';
        ctx.fillText('SIMULATED CCTV STREAM', cx, cy + 65);

        ctx.fillStyle = '#64748b';
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillText('CLICK "INGEST CCTV VIDEO" TO LOAD FEED', cx, cy + 82);
        ctx.textAlign = 'left';

        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.font = '10px "JetBrains Mono", monospace';
        const now = new Date();
        ctx.fillText(`${label} | STANDBY`, 12, 20);
        ctx.fillText(`${now.toTimeString().split(' ')[0]}`, canvas.width - 75, 20);

        animId = requestAnimationFrame(renderStandby);
    }

    renderStandby();
}

/**
 * Update Camera Card Counter Badges
 */
function updateLiveTelemetry(cameraId, data) {
    const card = document.getElementById(`card-${cameraId}`);
    if (!card) return;

    const countChips = card.querySelectorAll('.count-chip span');
    if (countChips.length >= 2) {
        countChips[0].textContent = data.people_count;
        countChips[1].textContent = data.vehicle_count;
    }
}

/**
 * Prepend a real AI Security Alert to the Live Alerts panel in real-time
 */
function prependLiveAlert(alert, cameraId) {
    const streamContainer = document.querySelector('.alert-stream-list');
    if (!streamContainer) return;

    if (document.getElementById(`alert-card-${alert.alert_id}`)) return;

    const card = document.createElement('div');
    card.className = `alert-item-card border-${alert.severity.toLowerCase()}`;
    card.id = `alert-card-${alert.alert_id}`;
    card.style.animation = 'flashBorder 1.5s infinite alternate';

    const sevBadgeClass = alert.severity === 'CRITICAL' ? 'bg-danger' : (alert.severity === 'HIGH' ? 'bg-warning text-dark' : 'bg-info text-dark');

    card.innerHTML = `
        <div class="alert-header">
            <span class="badge ${sevBadgeClass} font-monospace small">${alert.severity}</span>
            <span class="alert-meta">Just now</span>
        </div>
        <div class="alert-title">${alert.title}</div>
        <div class="d-flex align-items-center justify-content-between mt-2 pt-2 border-top border-secondary small font-monospace">
            <span class="text-cyan"><i class="bi bi-camera-video me-1"></i>${cameraId}</span>
            <span class="text-danger fw-bold">Threat: ${alert.threat_score}/100</span>
        </div>
    `;

    streamContainer.insertBefore(card, streamContainer.firstChild);

    // Dynamic toast notification
    showLiveToastNotification(alert, cameraId);

    // Audio alarm chime
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        const now = audioCtx.currentTime;
        osc.frequency.setValueAtTime(alert.severity === 'CRITICAL' ? 960 : 640, now);
        osc.frequency.setValueAtTime(alert.severity === 'CRITICAL' ? 1200 : 800, now + 0.15);
        gain.gain.setValueAtTime(0.09, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.4);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.4);
    } catch (e) {}
}

/**
 * On-Screen Live Threat Toast Notification
 */
function showLiveToastNotification(alert, cameraId) {
    let toastContainer = document.getElementById('liveThreatToastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'liveThreatToastContainer';
        toastContainer.style.position = 'fixed';
        toastContainer.style.top = '75px';
        toastContainer.style.right = '20px';
        toastContainer.style.zIndex = '9999';
        toastContainer.style.display = 'flex';
        toastContainer.style.flexDirection = 'column';
        toastContainer.style.gap = '10px';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const isCrit = alert.severity === 'CRITICAL';
    toast.className = `p-3 rounded shadow-lg border ${isCrit ? 'border-danger bg-dark' : 'border-warning bg-dark'}`;
    toast.style.minWidth = '290px';
    toast.style.maxWidth = '360px';
    toast.style.animation = 'fadeInRight 0.3s ease-out';
    toast.style.boxShadow = isCrit ? '0 0 20px rgba(244, 63, 94, 0.4)' : '0 0 15px rgba(245, 158, 11, 0.3)';

    toast.innerHTML = `
        <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="badge ${isCrit ? 'bg-danger' : 'bg-warning text-dark'} font-monospace small">
                <i class="bi bi-shield-exclamation me-1"></i> ${alert.severity} THREAT
            </span>
            <button type="button" class="btn-close btn-close-white" style="font-size: 0.65rem;" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="text-white small fw-bold mt-1">${alert.title}</div>
        <div class="d-flex align-items-center justify-content-between text-xs text-muted font-monospace mt-2 pt-1 border-top border-secondary">
            <span>Node: <strong class="text-cyan">${cameraId}</strong></span>
            <span class="text-danger fw-bold">Score: ${alert.threat_score}/100</span>
        </div>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}

/**
 * Fullscreen toggle for camera viewport
 */
function toggleFullscreen(feedCardId) {
    const card = document.getElementById(feedCardId);
    if (!card) return;
    if (!document.fullscreenElement) {
        card.requestFullscreen().catch(err => console.log(err));
    } else {
        document.exitFullscreen();
    }
}

/**
 * Real AI Video & Image Upload Inspector Form Handler
 */
document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('aiUploadForm');
    const progressEl = document.getElementById('analyzerProgress');
    const resultEl = document.getElementById('analyzerResult');
    const detectionsListEl = document.getElementById('resDetectionsList');
    const summaryEl = document.getElementById('resSummary');
    const timestampEl = document.getElementById('resTimestamp');
    const btnSubmit = document.getElementById('btnRunAnalysis');

    if (!uploadForm) return;

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fileInput = document.getElementById('analyzerFileInput');
        if (!fileInput || !fileInput.files || !fileInput.files[0]) {
            alert('Please select a video or image file to analyze.');
            return;
        }

        const formData = new FormData(uploadForm);

        if (progressEl) progressEl.classList.remove('d-none');
        if (resultEl) resultEl.classList.add('d-none');
        if (btnSubmit) btnSubmit.disabled = true;

        try {
            const response = await fetch('/cameras/analyze/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            const data = await response.json();

            if (progressEl) progressEl.classList.add('d-none');
            if (btnSubmit) btnSubmit.disabled = false;

            if (data.status === 'success') {
                if (summaryEl) summaryEl.textContent = data.summary;
                if (timestampEl) timestampEl.textContent = data.timestamp;

                if (detectionsListEl) {
                    detectionsListEl.innerHTML = '';
                    if (data.detections && data.detections.length > 0) {
                        data.detections.forEach((det) => {
                            const item = document.createElement('div');
                            item.className = 'd-flex align-items-center justify-content-between p-2 mb-2 rounded bg-dark border border-secondary';
                            item.innerHTML = `
                                <div>
                                    <span class="badge ${det.severity === 'CRITICAL' ? 'bg-danger' : 'bg-warning text-dark'} font-monospace me-2">${det.type}</span>
                                    <strong class="text-white">${det.label}</strong>
                                    <div class="text-muted text-xs font-monospace mt-1">${det.details}</div>
                                </div>
                                <div class="text-end">
                                    <span class="text-cyan font-monospace small d-block">Conf: ${det.confidence}</span>
                                    <span class="badge bg-secondary font-monospace mt-1">Risk: ${det.threat_score}/100</span>
                                </div>
                            `;
                            detectionsListEl.appendChild(item);
                        });
                    } else {
                        detectionsListEl.innerHTML = '<div class="text-success small p-2"><i class="bi bi-shield-check me-1"></i> No perimeter breaches or suspicious activity detected.</div>';
                    }
                }

                if (resultEl) resultEl.classList.remove('d-none');
            } else {
                alert('Analysis error: ' + (data.message || 'Failed to process file.'));
            }
        } catch (err) {
            if (progressEl) progressEl.classList.add('d-none');
            if (btnSubmit) btnSubmit.disabled = false;
            console.error('AI Analysis failed:', err);
            alert('Failed to connect to AI Inference Engine.');
        }
    });
});
