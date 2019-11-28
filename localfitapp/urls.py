# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import GVAMonitorDataViewSet, GVAMonitorFileUpload


router = routers.DefaultRouter()
router.register(r'gvamonitor', GVAMonitorDataViewSet)
router.register(r'gvamonitorupload', GVAMonitorFileUpload)

urlpatterns = [
    path('', include(router.urls)),  # routers above
]
