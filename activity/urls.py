# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from .views import ActivityFileUpload, ActivityViewSet


router = routers.DefaultRouter()
router.register(r'upload', ActivityFileUpload)
router.register(r'data', ActivityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
