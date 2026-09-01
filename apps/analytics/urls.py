from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_index, name='index'),
    path('api/data/', views.analytics_data_api, name='data_api'),
]
