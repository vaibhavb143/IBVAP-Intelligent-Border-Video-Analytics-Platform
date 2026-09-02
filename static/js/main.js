/**
 * IBVAP — Intelligent Border Video Analytics Platform
 * Global Command Center Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Military / IST Clock
    function updateClock() {
        const clockEl = document.getElementById('liveClock');
        if (!clockEl) return;
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const dateStr = now.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
        clockEl.textContent = `${hours}:${minutes}:${seconds} IST | ${dateStr}`;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // 2. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('socSidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // 3. Theme Toggle (Light / Dark Mode)
    const themeBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const themeLabel = document.getElementById('themeLabel');

    function syncThemeUI(theme) {
        if (themeIcon && themeLabel) {
            if (theme === 'light') {
                themeIcon.className = 'bi bi-sun-fill text-warning';
                themeLabel.textContent = 'LIGHT';
                if (themeBtn) themeBtn.className = 'btn btn-outline-primary btn-sm d-flex align-items-center gap-1.5 text-dark border-primary bg-light px-2.5 py-1 rounded-pill shadow-sm';
            } else {
                themeIcon.className = 'bi bi-moon-stars-fill text-warning';
                themeLabel.textContent = 'DARK';
                if (themeBtn) themeBtn.className = 'btn btn-outline-secondary btn-sm d-flex align-items-center gap-1.5 text-white border-secondary bg-dark bg-opacity-50 px-2.5 py-1 rounded-pill';
            }
        }
    }

    const currentTheme = localStorage.getItem('ibvap-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    syncThemeUI(currentTheme);

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', nextTheme);
            localStorage.setItem('ibvap-theme', nextTheme);
            syncThemeUI(nextTheme);
        });
    }

    // 4. Auto dismiss toasts after 4 seconds
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });
});

/**
 * Global CSRF Token Helper
 */
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
