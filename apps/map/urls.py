from django.urls import path
from . import views

app_name = 'map'

urlpatterns = [
    path('', views.map_index, name='index'),
]
