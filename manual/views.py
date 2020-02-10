# stdlib

# 3rd Party
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal
from .serializers import Vo2MaxSerializer
from .models import ManualStats


@api_view(['GET'])
def vo2_max(request):
    try:
        data = ManualStats.objects.first()
        serializer = Vo2MaxSerializer(data)
        return Response(serializer.data)
    except ManualStats.DoesNotExist:
        return HttpResponse(status=404)
