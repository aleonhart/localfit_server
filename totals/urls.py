# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from . import views


router = routers.DefaultRouter()
router.register(r'upload', views.TotalsFileUpload)

urlpatterns = [
    path('', include(router.urls)),
]
