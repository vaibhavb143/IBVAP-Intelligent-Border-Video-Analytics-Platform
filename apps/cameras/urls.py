from django.urls import path
from . import views

app_name = 'cameras'

urlpatterns = [
    path('', views.camera_list, name='list'),
    path('add/', views.add_camera, name='add'),
    path('analyze/', views.analyze_media_api, name='analyze'),
    path('live-inference/', views.live_frame_inference_api, name='live_inference'),
    path('<int:pk>/', views.camera_detail, name='detail'),
    path('<int:pk>/toggle-module/', views.toggle_ai_module, name='toggle_module'),
]
