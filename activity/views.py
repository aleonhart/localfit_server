# 3rd Party
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from fitparse import FitFile

# Internal
from .serializers import ActivityWalkFileSerializer
from .upload_serializers import (ActivityWalkFileUploadSerializer, ActivityYogaFileUploadSerializer,
                                 ActivityStairClimbingFileUploadSerializer, ActivityCardioFileUploadSerializer,
                                 ActivityRunFileUploadSerializer)
from .models import WalkData, ActivityFile


class ActivityViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = ActivityFile.objects.all().order_by('-session__start_time_utc')
    serializer_class = ActivityWalkFileSerializer
    lookup_field = 'filename'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ActivityWalkFileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ActivityWalkFileSerializer(queryset, many=True)
        return Response(serializer.data)


class ActivityFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """
    When the user uploads an ANT FIT ACTIVITY file, it will not be clear
    to them what type of activity they are uploading. We will have to
    distinguish the activity ("sport") type here, and select the
    appropriate serializer for that activity.
    """

    queryset = WalkData.objects.all()

    SPORT_TO_SERIALIZER = {
        (1, 0): ActivityRunFileUploadSerializer,              # Run: generic
        (11, 0): ActivityWalkFileUploadSerializer,            # walk
        (10, 43): ActivityYogaFileUploadSerializer,           # yoga
        (4, 16): ActivityStairClimbingFileUploadSerializer,   # Fitness Equipment: Stair Climbing
        (10, 26): ActivityCardioFileUploadSerializer,  # Training: Cardio (Beat Saber)
    }

    def _get_serializer_by_sport(self, kwargs):
        file_path = kwargs.get('file')
        if not file_path:
            raise ValidationError({"file": "Please provide a file path"})

        try:
            fit_file = FitFile(file_path)
        except FileNotFoundError:
            raise ValidationError({"file": "File does not exist"})
        sport_data = [r for r in fit_file.get_messages('sport') if r.type == 'data'][0]
        try:
            serializer = self.SPORT_TO_SERIALIZER[(sport_data.get("sport").raw_value, sport_data.get("sub_sport").raw_value)]
        except KeyError:
            raise ValidationError({"file": "Unsupported sport"})
        return serializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self._get_serializer_by_sport(kwargs['data'])
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as e:
            return Response(serializer.data, status=HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
