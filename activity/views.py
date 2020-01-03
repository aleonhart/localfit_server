# 3rd Party
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.db import IntegrityError

# Internal
from .serializers import ActivityFileUploadSerializer
from .models import ActivityWalkData


class ActivityFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):

    queryset = ActivityWalkData.objects.all()
    serializer_class = ActivityFileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            return Response(serializer.data, status=HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
