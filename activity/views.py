# 3rd Party
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from fitparse import FitFile

# Internal
from .serializers import ActivityWalkFileUploadSerializer, ActivityYogaFileUploadSerializer, ActivityWalkFileDetailSerializer, ActivityWalkFileListSerializer
from .models import WalkData, ActivityFile


class ActivityViewSet(viewsets.GenericViewSet,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin):

    queryset = ActivityFile.objects.all()
    serializer_class = ActivityWalkFileDetailSerializer
    lookup_field = 'filename'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ActivityWalkFileListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ActivityWalkFileListSerializer(queryset, many=True)
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
        (11, 0): ActivityWalkFileUploadSerializer,   # walk
        (10, 43): ActivityYogaFileUploadSerializer,  # yoga
    }

    def _get_serializer_by_sport(self, kwargs):
        file_path = kwargs.get('file')
        if not file_path:
            raise ValidationError({"file": "File must be provided"})

        fit_file = FitFile(file_path)
        sport_data = [r for r in fit_file.get_messages('sport') if r.type == 'data'][0]
        return self.SPORT_TO_SERIALIZER[(sport_data.get("sport").raw_value, sport_data.get("sub_sport").raw_value)]

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
