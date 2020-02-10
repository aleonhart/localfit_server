# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('vo2/', views.vo2_max),
]
