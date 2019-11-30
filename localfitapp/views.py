# STDLIB
import csv

# 3rd Party
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

# Internal
from .serializers import GVAMonitorFileUploadSerializer, StressDataSerializer
from .models import GVAMonitorStressData


@api_view(['GET'])
def stress_list(request):
    # TODO time bounds
    stress_data = GVAMonitorStressData.objects.all().order_by('-stress_level_time')
    serializer = StressDataSerializer(data=stress_data, many=True)
    return JsonResponse(serializer.data, safe=False)


class GVAMonitorFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """
    TODO filter and only show a day of data at a time
    objects.filter(stress_level_time__gt="2019-10-26 00:00:00", stress_level_time__lt="2019-10-27 00:00:00")
    """
    queryset = GVAMonitorStressData.objects.all().order_by('gvamonitordata_id')
    serializer_class = GVAMonitorFileUploadSerializer

