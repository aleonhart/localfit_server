from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('app/', include(('localfitapp.urls', 'localfitapp'), namespace='localfitapp')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
