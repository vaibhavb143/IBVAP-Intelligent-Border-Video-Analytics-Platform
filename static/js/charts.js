/**
 * IBVAP Analytics Intelligence Charts
 * Powered by Chart.js with SOC Dark Theme Palette
 */

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/analytics/api/data/');
        const data = await response.json();
        initCharts(data);
    } catch (err) {
        console.error("Failed to load analytics data:", err);
    }
});

function initCharts(data) {
    // Chart Default Styles
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';

    // 1. Events by Hour (Line / Area)
    const ctxHourly = document.getElementById('chartHourlyEvents');
    if (ctxHourly) {
        new Chart(ctxHourly, {
            type: 'line',
            data: {
                labels: data.hourly_events.labels,
                datasets: [{
                    label: 'Detected Events',
                    data: data.hourly_events.data,
                    borderColor: '#00f2fe',
                    backgroundColor: 'rgba(0, 242, 254, 0.12)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#00f2fe',
                    pointRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. Threat Level Distribution (Doughnut)
    const ctxThreat = document.getElementById('chartThreatDistribution');
    if (ctxThreat) {
        new Chart(ctxThreat, {
            type: 'doughnut',
            data: {
                labels: data.threat_distribution.labels,
                datasets: [{
                    data: data.threat_distribution.data,
                    backgroundColor: ['#f43f5e', '#f97316', '#f59e0b', '#10b981'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15 } }
                },
                cutout: '70%'
            }
        });
    }

    // 3. Camera Activity (Bar)
    const ctxCamera = document.getElementById('chartCameraActivity');
    if (ctxCamera) {
        new Chart(ctxCamera, {
            type: 'bar',
            data: {
                labels: data.camera_activity.labels,
                datasets: [{
                    label: 'Total Incidents Logged',
                    data: data.camera_activity.data,
                    backgroundColor: 'rgba(2, 132, 199, 0.7)',
                    borderColor: '#00f2fe',
                    borderWidth: 1,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 4. Detection Types Breakdown (Radar / Polar)
    const ctxDetection = document.getElementById('chartDetectionTypes');
    if (ctxDetection) {
        new Chart(ctxDetection, {
            type: 'bar',
            data: {
                labels: data.detection_types.labels,
                datasets: [{
                    label: 'Detections Count',
                    data: data.detection_types.data,
                    backgroundColor: ['#00f2fe', '#38bdf8', '#f43f5e', '#a855f7', '#f59e0b'],
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 5. ANPR Trends (Grouped Bar)
    const ctxAnpr = document.getElementById('chartAnprTrends');
    if (ctxAnpr) {
        new Chart(ctxAnpr, {
            type: 'bar',
            data: {
                labels: data.anpr_trends.labels,
                datasets: [
                    {
                        label: 'Total Vehicles Scanned',
                        data: data.anpr_trends.scanned,
                        backgroundColor: 'rgba(56, 189, 248, 0.4)',
                        borderColor: '#38bdf8',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Watchlist Matches',
                        data: data.anpr_trends.matches,
                        backgroundColor: 'rgba(244, 63, 94, 0.8)',
                        borderColor: '#f43f5e',
                        borderWidth: 1,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 6. Weekly Alert Severity Trends (Stacked Bar)
    const ctxWeekly = document.getElementById('chartWeeklyAlerts');
    if (ctxWeekly) {
        new Chart(ctxWeekly, {
            type: 'bar',
            data: {
                labels: data.weekly_alerts.labels,
                datasets: [
                    {
                        label: 'Critical',
                        data: data.weekly_alerts.critical,
                        backgroundColor: '#f43f5e',
                        borderRadius: 2,
                    },
                    {
                        label: 'High Risk',
                        data: data.weekly_alerts.high,
                        backgroundColor: '#f97316',
                        borderRadius: 2,
                    },
                    {
                        label: 'Medium Risk',
                        data: data.weekly_alerts.medium,
                        backgroundColor: '#f59e0b',
                        borderRadius: 2,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    x: { stacked: true, grid: { display: false } },
                    y: { stacked: true, beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                }
            }
        });
    }
}
