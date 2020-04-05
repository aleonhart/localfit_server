# stdlib
from datetime import datetime, timedelta

# 3rd Party
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

# Internal
from .models import ActivityFile, Session, ActivityData
from localfitserver.utils import (
    format_timespan_for_display,
    format_distance_for_display,
    format_date_for_display,
    format_date_for_calendar_heat_map,
    calculate_geographic_midpoint)
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
    # session = ActivityMapSessionSerializer(many=True, read_only=True)
    activitydata = ActivityWalkDataSerializer(many=True, read_only=True)

    def format_session_data(self, activity, secondary_activity):
        data = {}
        session = Session.objects.get(file=activity)
        # data['start_time_utc_dt'] = session.start_time_utc
        # data['start_time_utc'] = session.start_time_utc.strftime("%I:%M%p, %A, %B %d, %Y")
        # data['total_elapsed_time'] = format_timespan_for_display(session.total_elapsed_time)
        # data['total_distance'] = format_distance_for_display(session.total_distance)
        # data['total_calories'] = session.total_calories

        if secondary_activity:
            secondary_session = Session.objects.get(file=secondary_activity)
            data['total_elapsed_time'] = format_timespan_for_display(session.total_elapsed_time + secondary_session.total_elapsed_time)
            data['total_distance'] = format_distance_for_display(session.total_distance + secondary_session.total_distance)
            data['total_calories'] = session.total_calories + secondary_session.total_calories

        return data

    @property
    def data(self):
        ret = super().data
        session_data = self.format_session_data(self.instance, self.instance.secondary_activity)
        ret.update(**session_data)
        ret['activitydata'] = list(filter((None).__ne__, ret['activitydata']))
        ret['midpoint_lat_deg'], ret['midpoint_long_deg'] = calculate_geographic_midpoint(ret['activitydata'])
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['session', 'activitydata']


class ActivityMetaDataSerializer(serializers.ModelSerializer):

    def format_session_data(self, activity, secondary_activity):
        data = {}
        session = Session.objects.get(file=activity)
        data['start_time_utc_dt'] = session.start_time_utc
        data['start_time_utc'] = session.start_time_utc.strftime("%I:%M%p, %A, %B %d, %Y")
        data['total_elapsed_time'] = format_timespan_for_display(session.total_elapsed_time)
        data['total_distance'] = format_distance_for_display(session.total_distance)
        data['total_calories'] = session.total_calories
        data['start_location'] = session.start_location

        if secondary_activity:
            secondary_session = Session.objects.get(file=secondary_activity)
            data['total_elapsed_time'] = format_timespan_for_display(session.total_elapsed_time + secondary_session.total_elapsed_time)
            data['total_distance'] = format_distance_for_display(session.total_distance + secondary_session.total_distance)
            data['total_calories'] = session.total_calories + secondary_session.total_calories

        return data

    @property
    def data(self):
        session_data = self.format_session_data(self.instance, self.instance.secondary_activity)
        ret = super().data
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['activity_type', 'start_time_utc', 'session', 'activity_collection']


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


class TopActivitiesListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        files = super(TopActivitiesListSerializer, self).data
        files
        for file in files:
            session_data = file.pop('session')[0]
            file.update(**session_data)
        return ReturnList(files, serializer=self)


class TopActivitiesSerializer(serializers.Serializer):

    class Meta:
        model = ActivityData
        list_serializer_class = TopActivitiesListSerializer
        fields = '__all__'


class ActivitiesCalendarListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        activities = super(ActivitiesCalendarListSerializer, self).data
        year = self._kwargs['context']['request'].query_params['year']
        response = {
            'start_date': datetime.strptime(year, "%Y"),
            'end_date': (datetime.strptime(year, "%Y") + timedelta(days=364)).strftime("%Y-%m-%d"),
            'last_year': (datetime.strptime(year, "%Y") + timedelta(days=-365)).strftime("%Y"),
            'next_year': (datetime.strptime(year, "%Y") + timedelta(days=365)).strftime("%Y"),
            'activities': activities,
        }
        return ReturnDict(response, serializer=self)


class ActivitiesCalendarSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(ActivitiesCalendarSerializer, self).to_representation(instance)
        ret['date'] = format_date_for_calendar_heat_map(instance.start_time_utc)
        return ret

    class Meta:
        model = ActivityFile
        list_serializer_class = ActivitiesCalendarListSerializer
        fields = ['activity_type', 'start_time_utc', 'filename']
