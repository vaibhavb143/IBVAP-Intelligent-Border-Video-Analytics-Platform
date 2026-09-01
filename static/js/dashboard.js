/**
 * IBVAP Dashboard - Camera Feed Controller & Tactical Canvas Stream Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    initWebcamFeed('BOP-01');
    initSimulatedFeed('canvas-BOP-02', 'BOP-02 (Eastern Lowlands)', 'normal');
    initSimulatedFeed('canvas-BOP-03', 'BOP-03 (Restricted Outpost)', 'thermal');
    initSimulatedFeed('canvas-GATE-01', 'GATE-01 (Main Checkpost)', 'anpr');
});

/**
 * Initialize BOP-01 Webcam Stream
 */
function initWebcamFeed(cameraId) {
    const videoEl = document.getElementById(`video-${cameraId}`);
    const placeholder = document.getElementById(`placeholder-${cameraId}`);
    const toggleBtn = document.getElementById(`btn-webcam-${cameraId}`);
    let stream = null;

    async function startCamera() {
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: { ideal: 1280 }, height: { ideal: 720 } },
                    audio: false
                });
                if (videoEl) {
                    videoEl.srcObject = stream;
                    videoEl.play();
                    videoEl.style.display = 'block';
                    if (placeholder) placeholder.style.display = 'none';
                    if (toggleBtn) {
                        toggleBtn.innerHTML = '<i class="bi bi-camera-video-off"></i> Stop Webcam';
                        toggleBtn.classList.remove('btn-soc-primary');
                        toggleBtn.classList.add('btn-soc-secondary');
                    }
                }
            }
        } catch (err) {
            console.warn("Webcam access unavailable or permission denied:", err);
            // Gracefully render canvas simulation for BOP-01 if webcam isn't physically attached
            initSimulatedFeed(`canvas-${cameraId}`, 'BOP-01 Forward Outpost (Live Simulated)', 'live');
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            if (videoEl) videoEl.style.display = 'none';
            if (placeholder) placeholder.style.display = 'flex';
            if (toggleBtn) {
                toggleBtn.innerHTML = '<i class="bi bi-camera-video"></i> Start Webcam';
                toggleBtn.classList.remove('btn-soc-secondary');
                toggleBtn.classList.add('btn-soc-primary');
            }
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            if (stream) stopCamera();
            else startCamera();
        });
    }

    // Try auto-start on load
    startCamera();
}

/**
 * Animated Tactical Surveillance Canvas Generator for Simulated Feeds
 */
function initSimulatedFeed(canvasId, label, mode) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    canvas.width = 640;
    canvas.height = 360;

    let tick = 0;
    let scanY = 0;
    let objX = 180;
    let objDirection = 1;

    function render() {
        tick++;
        ctx.fillStyle = '#050a14';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Background terrain / border gradient simulation
        const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
        if (mode === 'thermal') {
            grad.addColorStop(0, '#040d1a');
            grad.addColorStop(1, '#0a223a');
        } else {
            grad.addColorStop(0, '#060d1b');
            grad.addColorStop(1, '#0f172a');
        }
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Grid lines
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.08)';
        ctx.lineWidth = 1;
        for (let x = 0; x < canvas.width; x += 40) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += 40) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }

        // Animated Radar Scan Line
        scanY = (scanY + 1.5) % canvas.height;
        ctx.fillStyle = 'rgba(0, 242, 254, 0.08)';
        ctx.fillRect(0, scanY, canvas.width, 4);

        // Virtual Fence Line for BOP-03 / Sector 3
        if (mode === 'thermal') {
            ctx.strokeStyle = '#f43f5e';
            ctx.setLineDash([8, 6]);
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, 240);
            ctx.lineTo(canvas.width, 240);
            ctx.stroke();
            ctx.setLineDash([]);
            
            ctx.fillStyle = 'rgba(244, 63, 94, 0.8)';
            ctx.font = '10px "JetBrains Mono"';
            ctx.fillText('⚡ VIRTUAL PERIMETER FENCE [BREACH DETECTED]', 20, 230);
        }

        // Dynamic Object Bounding Boxes
        objX += 0.8 * objDirection;
        if (objX > 420) objDirection = -1;
        if (objX < 140) objDirection = 1;

        if (mode === 'thermal') {
            // Intrusion Person Box
            ctx.strokeStyle = '#f43f5e';
            ctx.lineWidth = 2;
            ctx.strokeRect(objX, 150, 48, 100);
            ctx.fillStyle = 'rgba(244, 63, 94, 0.15)';
            ctx.fillRect(objX, 150, 48, 100);
            
            // Label
            ctx.fillStyle = '#f43f5e';
            ctx.font = '10px "JetBrains Mono"';
            ctx.fillText('INTRUSION 92%', objX, 142);
        } else if (mode === 'anpr') {
            // Vehicle Box
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 2;
            ctx.strokeRect(objX, 160, 140, 80);
            
            ctx.fillStyle = '#f59e0b';
            ctx.font = '10px "JetBrains Mono"';
            ctx.fillText('VEHICLE [MH20AB1234]', objX, 152);
            ctx.fillStyle = '#00f2fe';
            ctx.fillText('ANPR CONFIDENCE: 96%', objX, 255);
        } else {
            // Normal patrol object
            ctx.strokeStyle = '#00f2fe';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(objX, 170, 40, 85);
            ctx.fillStyle = '#00f2fe';
            ctx.font = '10px "JetBrains Mono"';
            ctx.fillText('PERSON 94%', objX, 162);
        }

        // Telemetry Overlay
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.font = '11px "JetBrains Mono"';
        const now = new Date();
        ctx.fillText(`REC: SIM-0${tick % 9} | FPS: 30.0 | ISO: 800`, 16, 24);
        ctx.fillText(`${now.toISOString().substring(11, 19)}.${Math.floor(now.getMilliseconds() / 100)}`, canvas.width - 110, 24);

        requestAnimationFrame(render);
    }
    render();
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
