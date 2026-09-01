from django.urls import path
from . import views

app_name = 'settings_app'

urlpatterns = [
    path('', views.settings_index, name='index'),
]
