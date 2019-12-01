# 3rd Party
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.db import IntegrityError

# Internal
from .serializers import MonitorStressFileUploadSerializer, StressDataSerializer
from .models import MonitorStressData


class StressList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = MonitorStressData.objects.all()
    serializer_class = StressDataSerializer

    def get_queryset(self):
        queryset = MonitorStressData.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(stress_level_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(stress_level_time__lt=end_date)
        return queryset

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class MonitorFileStressUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):

    queryset = MonitorStressData.objects.all()
    serializer_class = MonitorStressFileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return Response(serializer.data, status=HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
