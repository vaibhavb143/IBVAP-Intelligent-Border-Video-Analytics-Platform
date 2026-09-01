/**
 * IBVAP Alerts Controller
 */

async function handleAlertAction(url, alertCardId, actionType) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            }
        });

        if (response.ok) {
            const card = document.getElementById(alertCardId);
            if (card) {
                if (actionType === 'resolve') {
                    card.style.opacity = '0.5';
                    const badge = card.querySelector('.alert-status-badge');
                    if (badge) {
                        badge.className = 'badge bg-secondary text-white';
                        badge.textContent = 'RESOLVED';
                    }
                } else if (actionType === 'acknowledge') {
                    const badge = card.querySelector('.alert-status-badge');
                    if (badge) {
                        badge.className = 'badge bg-warning text-dark';
                        badge.textContent = 'ACKNOWLEDGED';
                    }
                }
            }
        }
    } catch (err) {
        console.error("Alert action failed:", err);
    }
}
