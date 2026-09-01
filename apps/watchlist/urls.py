from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.watchlist_list, name='list'),
    path('add-vehicle/', views.add_vehicle, name='add'),
    path('<int:pk>/delete-vehicle/', views.delete_vehicle, name='delete'),
    path('add-person/', views.add_person, name='add_person'),
    path('<int:pk>/delete-person/', views.delete_person, name='delete_person'),
]
