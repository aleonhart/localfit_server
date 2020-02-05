# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import MonitorFileUpload, StressList, HeartRateList


router = routers.DefaultRouter()
router.register(r'upload', MonitorFileUpload)
router.register(r'stress_data', StressList)
router.register(r'heart_rate', HeartRateList)


urlpatterns = [
    path('', include(router.urls)),
]
