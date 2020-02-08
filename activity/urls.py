# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from . import views


router = routers.DefaultRouter()
router.register(r'upload', views.ActivityFileUpload)

urlpatterns = [
    path('', include(router.urls)),
    path('meta/', views.activities),
    path('calendar/', views.activities_calendar),
    path('meta/<filename>/', views.activity),
    path('map/<filename>/', views.activity_map),
    path('altitude/<filename>/', views.activity_altitude),
    path('heart_rate/<filename>/', views.activity_heart_rate),
]
