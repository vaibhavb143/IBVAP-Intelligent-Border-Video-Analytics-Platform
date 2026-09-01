from django.urls import path
from . import views

app_name = 'anpr'

urlpatterns = [
    path('', views.anpr_list, name='list'),
]
