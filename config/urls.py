from django.contrib import admin
from django.urls import path, include
from face_tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('trigger/', views.trigger, name='trigger'),  # This line will now work
]
