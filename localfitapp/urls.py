# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import GVAMonitorFileUpload, stress_list


router = routers.DefaultRouter()
router.register(r'gvamonitorupload', GVAMonitorFileUpload)

urlpatterns = [
    path('', include(router.urls)),
    path('stress_data/', stress_list),
]
