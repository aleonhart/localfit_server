# stdlib
from datetime import datetime, timedelta

# 3rd Party
from django.http import HttpResponse
from django.utils import timezone
from fitparse import FitFile
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
import pytz

# Internal
from .serializers import (ActivityMapDataSerializer, ActivityMetaDataSerializer, ActivityAltitudeSerializer,
                          ActivityHeartRateSerializer, ActivitiesSerializer, ActivitiesCalendarSerializer)
from .upload_serializers import (ActivityWalkFileUploadSerializer, ActivityYogaFileUploadSerializer,
                                 ActivityStairClimbingFileUploadSerializer, ActivityCardioFileUploadSerializer,
                                 ActivityRunFileUploadSerializer, ActivityTreadmillFileUploadSerializer,
                                 ActivityEllipticalFileUploadSerializer)
from .models import ActivityData, ActivityFile
from localfitserver import settings


@api_view(['GET'])
def activity_heart_rate(request, filename):
    try:
        data = ActivityData.objects.filter(file__filename=filename).order_by('timestamp_utc')
        serializer = ActivityHeartRateSerializer(data, many=True)
        return Response(serializer.data)
    except ActivityFile.DoesNotExist:
        return HttpResponse(status=404)


@api_view(['GET'])
def activity_altitude(request, filename):
    try:
        data = ActivityData.objects.filter(file__filename=filename).order_by('timestamp_utc')
        serializer = ActivityAltitudeSerializer(data, many=True)
        return Response(serializer.data)
    except ActivityFile.DoesNotExist:
        return HttpResponse(status=404)


@api_view(['GET'])
def activity_map(request, filename):
    try:
        file = ActivityFile.objects.get(filename=filename)
    except ActivityFile.DoesNotExist:
        return HttpResponse(status=HTTP_404_NOT_FOUND)

    # not all files have GPS data
    if set(ActivityData.objects.filter(file=file).values_list('position_lat_sem', flat=True)) == {None}:
        return HttpResponse(status=HTTP_404_NOT_FOUND)

    serializer = ActivityMapDataSerializer(file)
    return Response(serializer.data)


@api_view(['GET'])
def activity(request, filename):
    try:
        data = ActivityFile.objects.get(filename=filename)
        serializer = ActivityMetaDataSerializer(data)
        return Response(serializer.data)
    except ActivityFile.DoesNotExist:
        return HttpResponse(status=404)


@api_view(['GET'])
def activities(request):
    try:
        year_str = request.query_params.get('year')
        if not year_str:
            raise ValidationError({'error': 'Please provide a year'})

        start_date_dt = timezone.make_aware(datetime.strptime(f'{year_str}-01-01', "%Y-%m-%d"),
                                            timezone=pytz.timezone(settings.TIME_ZONE))
        end_date_dt = start_date_dt + timedelta(days=366)
        data = ActivityFile.objects.filter(start_time_utc__gte=start_date_dt,
                                           start_time_utc__lt=end_date_dt).order_by('-start_time_utc')
        serializer = ActivitiesSerializer(data, many=True)
        return Response(serializer.data)
    except ActivityFile.DoesNotExist:
        return HttpResponse(status=404)


class ActivitiesCalendarList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = ActivityFile.objects.all()
    serializer_class = ActivitiesCalendarSerializer

    def get_queryset(self):
        year_str = self.request.query_params['year']
        start_date_dt = timezone.make_aware(datetime.strptime(f'{year_str}-01-01', "%Y-%m-%d"),
                                         timezone=pytz.timezone(settings.TIME_ZONE))
        end_date_dt = start_date_dt + timedelta(days=365)
        return ActivityFile.objects.filter(start_time_utc__gte=start_date_dt, start_time_utc__lt=end_date_dt)

    def list(self, request, *args, **kwargs):
        if not request.query_params.get('year'):
            raise ValidationError({'error': 'Please provide a year'})
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ActivityFileUpload(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """
    When the user uploads an ANT FIT ACTIVITY file, it will not be clear
    to them what type of activity they are uploading. We will have to
    distinguish the activity ("sport") type here, and select the
    appropriate serializer for that activity.
    """

    queryset = ActivityData.objects.all()

    SPORT_TO_SERIALIZER = {
        (1, 0): ActivityRunFileUploadSerializer,              # Run: generic
        (1, 1): ActivityTreadmillFileUploadSerializer,        # Run: Treadmill
        (4, 15): ActivityEllipticalFileUploadSerializer,      # Fitness Equipment: Elliptical
        (11, 0): ActivityWalkFileUploadSerializer,            # walk
        (10, 43): ActivityYogaFileUploadSerializer,           # yoga
        (4, 16): ActivityStairClimbingFileUploadSerializer,   # Fitness Equipment: Stair Climbing
        (10, 26): ActivityCardioFileUploadSerializer,  # Training: Cardio (Beat Saber)
    }

    def _get_serializer_by_sport(self, kwargs):
        sport_data = [r for r in kwargs['fit_file'].get_messages('sport') if r.type == 'data'][0]
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
