# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import MonitorFileUpload, StressList, HeartRateList, RestingMetaList, StressRange, StepsList


router = routers.DefaultRouter()
router.register(r'upload', MonitorFileUpload)
router.register(r'steps', StepsList)
router.register(r'stress_data', StressList)
router.register(r'stress_range', StressRange)
router.register(r'heart_rate', HeartRateList)
router.register(r'resting_meta', RestingMetaList)


urlpatterns = [
    path('', include(router.urls)),
]
