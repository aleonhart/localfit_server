from django.urls import include, path
from rest_framework import routers


router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('manual/', include(('manual.urls', 'manual'), namespace='manual')),
    path('monitor/', include(('monitor.urls', 'monitor'), namespace='monitor')),
    path('activity/', include(('activity.urls', 'activity'), namespace='activity')),
    path('totals/', include(('totals.urls', 'totals'), namespace='totals')),
    path('records/', include(('records.urls', 'records'), namespace='records')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
