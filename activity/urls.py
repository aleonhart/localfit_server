# 3rd Party
from django.urls import include, path
from rest_framework import routers

# Internal
from . import views


router = routers.DefaultRouter()
router.register(r'upload', views.ActivityFileUpload)
router.register(r'info', views.ActivityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('info/', views.activity_list),
    path('altitude/<filename>/', views.activity_altitude),
]
