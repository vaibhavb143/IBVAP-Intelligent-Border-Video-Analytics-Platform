from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('<int:pk>/evidence/', views.event_evidence_api, name='evidence_api'),
]
