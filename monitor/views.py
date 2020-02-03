# stdlib
from datetime import datetime

# 3rd Party
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.db import IntegrityError
import pytz

# Internal
from .serializers import MonitorHeartRateFileUploadSerializer, StressDataSerializer, HeartRateDataSerializer
from .models import MonitorStressData, MonitorHeartRateData
from localfitserver import settings


class HeartRateList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = MonitorHeartRateData.objects.all()
    serializer_class = HeartRateDataSerializer

    def get_queryset(self):
        queryset = MonitorHeartRateData.objects.all()
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        if start_date_str:
            start_date_dt = timezone.make_aware(datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S"), timezone=pytz.timezone(settings.TIME_ZONE))
            queryset = queryset.filter(timestamp_utc__gte=start_date_dt.date())
        if end_date_str:
            end_date_dt = timezone.make_aware(datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S"), timezone=pytz.timezone(settings.TIME_ZONE))
            queryset = queryset.filter(timestamp_utc__lt=end_date_dt.date())
        return queryset

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class StressList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = MonitorStressData.objects.all()
    serializer_class = StressDataSerializer

    def get_queryset(self):
        queryset = MonitorStressData.objects.all()
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        if start_date_str:
            start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            queryset = queryset.filter(stress_level_time__gte=start_date_dt.date())
        if end_date_str:
            end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            queryset = queryset.filter(stress_level_time__lt=end_date_dt.date())
        return queryset

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class MonitorFileHeartRateUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):

    queryset = MonitorHeartRateData.objects.all()
    serializer_class = MonitorHeartRateFileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return Response(serializer.data, status=HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
