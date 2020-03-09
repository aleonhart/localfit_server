# stdlib
from datetime import datetime

# 3rd Party
from django.utils import timezone
from fitparse import FitFile
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
import pytz

# Internal
from .upload_serializers import MonitorFileUploadSerializer
from .serializers import StressDataSerializer, HeartRateDataSerializer, RestingMetaRateSerializer, PieChartSerializer, StepDataSerializer
from .models import StressData, HeartRateData, RestingMetRateData, StepData
from localfitserver import settings


class StepsList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = StepData.objects.all()
    serializer_class = StepDataSerializer

    def get_queryset(self):
        start_date = self.request.query_params['start_date']
        start_date_dt = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"), timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = self.request.query_params['end_date']
        end_date_dt = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"),
                                            timezone=pytz.timezone(settings.TIME_ZONE))
        return StepData.objects.filter(date__gte=start_date_dt, date__lte=end_date_dt)

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('start_date'):
            raise ValidationError({'error': 'Please provide a start_date'})

        if not request.query_params.get('end_date'):
            raise ValidationError({'error': 'Please provide an end_date'})

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class RestingMetaList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = RestingMetRateData.objects.all()
    serializer_class = RestingMetaRateSerializer

    def get_queryset(self):
        queryset = RestingMetRateData.objects.all()
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


class HeartRateList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = HeartRateData.objects.all()
    serializer_class = HeartRateDataSerializer

    def get_queryset(self):
        queryset = HeartRateData.objects.all()
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
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class StressRange(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = StressData.objects.all()
    serializer_class = PieChartSerializer

    def get_queryset(self):
        queryset = StressData.objects.all()
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        if start_date_str:
            start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            queryset = queryset.filter(stress_level_time_utc__gte=start_date_dt.date())
        if end_date_str:
            end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            queryset = queryset.filter(stress_level_time_utc__lt=end_date_dt.date())
        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class StressList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = StressData.objects.all()
    serializer_class = StressDataSerializer

    def get_queryset(self):
        queryset = StressData.objects.all()
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        if start_date_str:
            start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            queryset = queryset.filter(stress_level_time_utc__gte=start_date_dt.date())
        if end_date_str:
            end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            queryset = queryset.filter(stress_level_time_utc__lt=end_date_dt.date())
        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class MonitorFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):

    queryset = HeartRateData.objects.all()
    serializer_class = MonitorFileUploadSerializer

    def create(self, request, *args, **kwargs):
        if not request.FILES.get('file'):
            raise ValidationError({"file": "Please provide a file"})

        try:
            fit_file = FitFile(request.FILES['file'])
        except FileNotFoundError:
            raise ValidationError({"file": "File does not exist"})

        request.data['fit_file'] = fit_file
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
