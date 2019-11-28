# STDLIB
import csv

# 3rd Party
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

# Internal
from .serializers import GVAMonitorDataSerializer, GVAMonitorFileUploadSerializer
from .models import GVAMonitorFile, GVAMonitorData


class GVAMonitorDataViewSet(viewsets.ModelViewSet):
    queryset = GVAMonitorData.objects.all().order_by('gvamonitordata_id')
    serializer_class = GVAMonitorDataSerializer


class GVAMonitorFileUpload(viewsets.ModelViewSet):
    queryset = GVAMonitorData.objects.all().order_by('gvamonitordata_id')
    serializer_class = GVAMonitorFileUploadSerializer
