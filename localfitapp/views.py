# 3rd Party
from rest_framework import viewsets, mixins
from rest_framework.response import Response

# Internal
from .serializers import GVAMonitorFileUploadSerializer, StressDataSerializer
from .models import GVAMonitorStressData


class StressList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = GVAMonitorStressData.objects.all()
    serializer_class = StressDataSerializer

    def get_queryset(self):
        queryset = GVAMonitorStressData.objects.all()
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


class GVAMonitorFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):

    queryset = GVAMonitorStressData.objects.all().order_by('gvamonitordata_id')
    serializer_class = GVAMonitorFileUploadSerializer

