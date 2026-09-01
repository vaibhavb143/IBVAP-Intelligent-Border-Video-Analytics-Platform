"""
IBVAP URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('auth/', include('apps.accounts.urls')),
    path('cameras/', include('apps.cameras.urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('events/', include('apps.events.urls')),
    path('anpr/', include('apps.anpr.urls')),
    path('watchlist/', include('apps.watchlist.urls')),
    path('map/', include('apps.map.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('settings/', include('apps.settings_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
