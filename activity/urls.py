# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from . import views


router = routers.DefaultRouter()
router.register(r'upload', views.ActivityFileUpload)
router.register(r'calendar', views.ActivitiesCalendarList)

urlpatterns = [
    path('', include(router.urls)),
    path('meta/', views.activities),
    path('meta/<filename>/', views.activity),
    path('update/<filename>/', views.update_activity),
    path('map/<filename>/', views.activity_map),
    path('altitude/<filename>/', views.activity_altitude),
    path('heart_rate/<filename>/', views.activity_heart_rate),
    path('top/', views.top_activities),

]
