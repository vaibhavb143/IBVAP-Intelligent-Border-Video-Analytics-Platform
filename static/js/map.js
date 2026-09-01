/**
 * IBVAP Tactical Border Map Controller
 */

function selectMapNode(code, name, status, risk, threat, lat, lng) {
    const infoPanel = document.getElementById('mapTelemetryPanel');
    if (!infoPanel) return;

    let badgeClass = 'text-bg-success';
    if (risk === 'CRITICAL') badgeClass = 'bg-danger text-white';
    else if (risk === 'HIGH') badgeClass = 'bg-warning text-dark';
    else if (risk === 'MEDIUM') badgeClass = 'bg-info text-dark';

    infoPanel.innerHTML = `
        <div class="soc-card glow-cyan">
            <div class="d-flex align-items-center justify-content-between mb-3 border-bottom pb-2">
                <span class="fw-bold font-monospace text-info">${code}</span>
                <span class="badge ${badgeClass}">${risk} RISK</span>
            </div>
            <h6 class="fw-bold text-white mb-2">${name}</h6>
            <div class="d-flex flex-column gap-2 text-muted small font-monospace">
                <div><i class="bi bi-geo-alt text-cyan"></i> Coordinates: <span class="text-white">${lat}, ${lng}</span></div>
                <div><i class="bi bi-shield-exclamation text-danger"></i> Sector Threat Score: <span class="text-danger fw-bold">${threat} / 100</span></div>
                <div><i class="bi bi-camera-video text-success"></i> Optical Feeds: <span class="text-white">Active</span></div>
                <div><i class="bi bi-broadcast text-info"></i> Sensor Array: <span class="text-white">Virtual Fence / Thermal</span></div>
            </div>
            <div class="mt-3 pt-2 border-top d-flex gap-2">
                <a href="/cameras/" class="btn-soc-primary w-100 justify-content-center">
                    <i class="bi bi-eye"></i> View Sector Feeds
                </a>
            </div>
        </div>
    `;
}
