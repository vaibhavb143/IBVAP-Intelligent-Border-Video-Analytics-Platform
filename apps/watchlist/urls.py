from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.watchlist_list, name='list'),
    path('add/', views.add_vehicle, name='add'),
    path('<int:pk>/delete/', views.delete_vehicle, name='delete'),
]
