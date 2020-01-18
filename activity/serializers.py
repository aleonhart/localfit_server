# 3rd Party
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.utils.serializer_helpers import ReturnDict
from fitparse import FitFile

# Internal
from .models import ActivityFile, Session, WalkData, YogaData
from localfitserver.utils import (
    convert_ant_timestamp_to_unix_timestamp,
    convert_semicircles_to_degrees,
    convert_lat_long_to_location_name,
    format_timespan_for_display,
    format_distance_for_display,
    format_date_for_display)


class ActivityWalkDataSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super(ActivityWalkDataSerializer, self).to_representation(instance)
        if data['position_lat_deg'] and data['position_long_deg']:
            return {'lat': data['position_lat_deg'], 'lng': data['position_long_deg']} \
                if data['position_lat_deg'] and data['position_long_deg'] else None

    class Meta:
        model = WalkData
        fields = ['position_lat_deg', 'position_long_deg']


class ActivityWalkSessionSerializer(serializers.ModelSerializer):
    total_distance = serializers.DecimalField(max_digits=8, decimal_places=2)

    def to_representation(self, instance):
        data = super(ActivityWalkSessionSerializer, self).to_representation(instance)
        data['start_time_utc'] = format_date_for_display(data['start_time_utc']) if data.get('start_time_utc') else None
        data['total_elapsed_time'] = format_timespan_for_display(data['total_elapsed_time']) if data.get('total_elapsed_time') else None
        data['total_distance'] = format_distance_for_display(data['total_distance']) if data.get('total_distance') else None
        data['start_location'] = convert_lat_long_to_location_name(data['start_position_lat_deg'], data['start_position_long_deg']) if data.get('start_position_lat_deg') else None
        return data

    class Meta:
        model = Session
        fields = [
            'start_time_utc',
            'start_position_lat_deg',
            'start_position_long_deg',
            'total_elapsed_time',
            'total_distance',
            'total_strides',
            'total_calories',
        ]


class ActivityWalkFileListSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    @property
    def data(self):
        ret = super(ActivityWalkFileListSerializer, self).data
        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['activity_type', 'session']


class ActivityWalkFileDetailSerializer(serializers.ModelSerializer):
    activitywalkdata = ActivityWalkDataSerializer(many=True, read_only=True)
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    @property
    def data(self):
        """
        Front End expects this format for easy parsing by Google Maps API
        {
            data: {
                results: [
                    { lat: 41.365286, lng: -124.018488 },
                    { lat: 41.365236, lng: -124.018411 }
                ]
            }
        }
        """
        ret = super(ActivityWalkFileDetailSerializer, self).data
        # Filter out records that were recorded by the watch before GPS was enabled
        # TODO consider replacing the None with the starting coordinate if we need other data later
        ret['activitywalkdata'] = list(filter((None).__ne__, ret['activitywalkdata']))

        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['activity_type', 'activitywalkdata', 'session']


class BaseActivityFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    generic_fields = []
    time_fields = []
    gps_fields = []

    def _save_activity_file(self, filename):
        raise ValidationError("Child class must implement this method!")

    def _get_activity_session_data(self, fit_file):
        raise ValidationError("Child class must implement this method!")

    def validate(self, attrs):
        fit_file = FitFile(self.initial_data['file'])
        attrs['file'] = fit_file
        attrs['filename'] = self.initial_data['file'].split("/")[-1].split(".")[0]
        attrs['session_data'] = self._get_activity_session_data(fit_file)
        return attrs

    def create(self, validated_data):
        newfiledata = None
        with transaction.atomic():
            file = self._save_activity_file(validated_data['filename'])
            session = Session(file=file, **validated_data['session_data'])
            session.save()

            for record in validated_data['file'].get_messages('record'):
                rowdict = {'file': file}
                for record_data in record:
                    if record_data.name in self.generic_fields:
                        rowdict[record_data.name] = record_data.value
                    if record_data.name in self.time_fields:
                        rowdict[f'{record_data.name}_utc'] = convert_ant_timestamp_to_unix_timestamp(record_data.value)
                    if record_data.name in self.gps_fields:
                        rowdict[f'{record_data.name}_sem'] = record_data.value
                        rowdict[f'{record_data.name}_deg'] = convert_semicircles_to_degrees(record_data.value)

                newfiledata = self.Meta.model(**rowdict)
                newfiledata.save()

        return newfiledata

    class Meta:
        model = None


class ActivityWalkFileUploadSerializer(BaseActivityFileUploadSerializer):
    # TODO someday consider converting this to using ANT's file ids and field specifications
    # TODO can fitparse library "fields" value handle this?
    generic_fields = [
        'distance',
        'altitude',
        'speed',
        'heart_rate',
        'cadence',
        'fractional_cadence',
        'enhanced_altitude',
        'enhanced_speed'
    ]
    time_fields = [
        'timestamp'
    ]
    gps_fields = [
        'position_lat',
        'position_long'
    ]

    def _save_activity_file(self, filename):
        file = ActivityFile(filename=filename, activity_type='walk')
        file.save()
        return file

    def _get_activity_session_data(self, fit_file):
        session_data = [row for row in fit_file.get_messages('session')][0]
        return {
            'start_time_utc': convert_ant_timestamp_to_unix_timestamp(session_data.get('start_time').value),
            'start_position_lat_sem': session_data.get('start_position_lat').value,
            'start_position_long_sem': session_data.get('start_position_long').value,
            'start_position_lat_deg': convert_semicircles_to_degrees(session_data.get('start_position_lat').value),
            'start_position_long_deg': convert_semicircles_to_degrees(session_data.get('start_position_long').value),
            'total_elapsed_time': session_data.get('total_elapsed_time').value,
            'total_timer_time': session_data.get('total_timer_time').value,
            'total_distance': session_data.get('total_distance').value,
            'total_strides': session_data.get('total_strides').value,
            'total_calories': session_data.get('total_calories').value,
            'enhanced_avg_speed': session_data.get('enhanced_avg_speed').value,
            'avg_speed': session_data.get('avg_speed').value,
            'enhanced_max_speed': session_data.get('enhanced_max_speed').value,
            'max_speed': session_data.get('max_speed').value,
            'avg_power': session_data.get('avg_power').value,
            'max_power': session_data.get('max_power').value,
            'total_ascent': session_data.get('total_ascent').value,
            'total_descent': session_data.get('total_descent').value,
        }

    class Meta:
        model = WalkData


class ActivityYogaFileUploadSerializer(BaseActivityFileUploadSerializer):
    generic_fields = [
        'heart_rate',
    ]
    time_fields = [
        'timestamp'
    ]

    def _save_activity_file(self, filename):
        file = ActivityFile(filename=filename, activity_type='yoga')
        file.save()
        return file

    def _get_activity_session_data(self, fit_file):
        session_data = [row for row in fit_file.get_messages('session')][0]
        return {
            'start_time_utc': convert_ant_timestamp_to_unix_timestamp(session_data.get('start_time').value),
            'total_elapsed_time': session_data.get('total_elapsed_time').value,
            'total_timer_time': session_data.get('total_timer_time').value,
            'total_calories': session_data.get('total_calories').value,
            'avg_heart_rate': session_data.get('avg_heart_rate').value,
            'max_heart_rate': session_data.get('max_heart_rate').value,
        }

    class Meta:
        model = YogaData
