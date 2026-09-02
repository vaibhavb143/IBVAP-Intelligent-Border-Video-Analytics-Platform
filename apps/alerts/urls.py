from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.alert_list, name='list'),
    path('clear-all/', views.clear_all_alerts, name='clear_all'),
    path('<int:pk>/delete/', views.delete_alert, name='delete'),
    path('<int:pk>/acknowledge/', views.acknowledge_alert, name='acknowledge'),
    path('<int:pk>/resolve/', views.resolve_alert, name='resolve'),
]
