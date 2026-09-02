from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ANPRDetection
from apps.watchlist.models import WatchlistVehicle

@login_required
def anpr_list(request):
    detections = ANPRDetection.objects.all().select_related('camera')
    
    # Check if any watchlist matches
    recent_matches = detections.filter(is_watchlist_match=True)[:3]
    top_match = recent_matches.first() if recent_matches.exists() else None
    
    total_plates = detections.count()
    watchlist_matches_count = detections.filter(is_watchlist_match=True).count()
    vehicles_today = total_plates

    return render(request, 'anpr/index.html', {
        'detections': detections[:50],
        'top_match': top_match,
        'recent_matches': recent_matches,
        'total_plates': total_plates,
        'watchlist_matches_count': watchlist_matches_count,
        'vehicles_today': vehicles_today,
    })
