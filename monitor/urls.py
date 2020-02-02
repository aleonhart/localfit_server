# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import MonitorFileHeartRateUpload, StressList, HeartRateList


router = routers.DefaultRouter()
router.register(r'heart_rate/upload', MonitorFileHeartRateUpload)
router.register(r'stress_data', StressList)
router.register(r'heart_rate', HeartRateList)


urlpatterns = [
    path('', include(router.urls)),
]
