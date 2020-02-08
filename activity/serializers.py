# 3rd Party
from django.utils import timezone
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

# Internal
from .models import ActivityFile, Session, ActivityData
from localfitserver.utils import (
    format_timespan_for_display,
    format_distance_for_display,
    format_date_for_display,
    format_date_for_calendar_heat_map)
from localfitserver.base_serializers import BaseChartJSListSerializer


class ActivityHeartRateListSerializer(BaseChartJSListSerializer):
    chart_field = 'heart_rate'


class ActivityHeartRateSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        super(ActivityHeartRateSerializer, self).to_representation(instance)
        return instance

    class Meta:
        model = ActivityData
        list_serializer_class = ActivityHeartRateListSerializer
        fields = ['timestamp_utc', 'heart_rate']


class ActivityAltitudeListSerializer(BaseChartJSListSerializer):
    chart_field = 'altitude'


class ActivityAltitudeSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        super(ActivityAltitudeSerializer, self).to_representation(instance)
        return instance

    class Meta:
        model = ActivityData
        list_serializer_class = ActivityAltitudeListSerializer
        fields = ['timestamp_utc', 'altitude', 'enhanced_altitude']


class ActivityWalkDataSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super(ActivityWalkDataSerializer, self).to_representation(instance)
        if data['position_lat_deg'] and data['position_long_deg']:
            return {'lat': data['position_lat_deg'], 'lng': data['position_long_deg']} \
                if data['position_lat_deg'] and data['position_long_deg'] else None

    class Meta:
        model = ActivityData
        fields = ['position_lat_deg', 'position_long_deg']


class ActivityWalkSessionSerializer(serializers.ModelSerializer):
    total_distance = serializers.DecimalField(max_digits=8, decimal_places=2)

    def to_representation(self, instance):
        data = super(ActivityWalkSessionSerializer, self).to_representation(instance)
        data['start_time_utc_dt'] = data['start_time_utc']
        data['start_time_utc'] = format_date_for_display(data['start_time_utc']) if data.get('start_time_utc') else None
        data['total_elapsed_time'] = format_timespan_for_display(data['total_elapsed_time']) if data.get('total_elapsed_time') else None
        data['total_distance'] = format_distance_for_display(data['total_distance']) if data.get('total_distance') else None
        return data

    class Meta:
        model = Session
        fields = [
            'start_time_utc',
            'start_position_lat_deg',
            'start_position_long_deg',
            'start_location',
            'total_elapsed_time',
            'total_distance',
            'total_strides',
            'total_calories',
        ]


class ActivityMapSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = [
            'start_position_lat_deg',
            'start_position_long_deg',
        ]


class ActivityMapDataSerializer(serializers.ModelSerializer):
    session = ActivityMapSessionSerializer(many=True, read_only=True)
    activitydata = ActivityWalkDataSerializer(many=True, read_only=True)

    @property
    def data(self):
        ret = super().data
        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        ret['activitydata'] = list(filter((None).__ne__, ret['activitydata']))
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['session', 'activitydata']


class ActivityMetaDataSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    @property
    def data(self):
        ret = super().data
        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['activity_type', 'start_time_utc', 'session']


class ActivitiesListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        files = super(ActivitiesListSerializer, self).data
        for file in files:
            session_data = file.pop('session')[0]
            file.update(**session_data)
        return ReturnList(files, serializer=self)


class ActivitiesSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    class Meta:
        model = ActivityFile
        list_serializer_class = ActivitiesListSerializer
        fields = ['filename', 'activity_type', 'activity_category', 'start_time_utc', 'session']


class ActivitiesCalendarListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        files = super(ActivitiesCalendarListSerializer, self).data
        return ReturnList(files, serializer=self)


class ActivitiesCalendarSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(ActivitiesCalendarSerializer, self).to_representation(instance)
        ret['date'] = format_date_for_calendar_heat_map(instance.start_time_utc)
        return ret

    class Meta:
        model = ActivityFile
        list_serializer_class = ActivitiesCalendarListSerializer
        fields = ['activity_type', 'start_time_utc']
