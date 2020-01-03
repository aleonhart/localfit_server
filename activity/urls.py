# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import ActivityFileUpload


router = routers.DefaultRouter()
router.register(r'upload', ActivityFileUpload)

urlpatterns = [
    path('', include(router.urls)),
]
