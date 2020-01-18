# 3rd Party
from django.db import transaction
from rest_framework import serializers
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict
from fitparse import FitFile

# Internal
from .models import ActivityWalkFile, ActivityWalkSession, ActivityWalkData
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
        model = ActivityWalkData
        fields = ['position_lat_deg', 'position_long_deg']


class ActivityWalkSessionSerializer(serializers.ModelSerializer):

    """
    ret['total_distance'] = format_distance_for_display(ret['total_distance'])

    """
    total_distance = serializers.DecimalField(max_digits=8, decimal_places=2)

    def to_representation(self, instance):
        data = super(ActivityWalkSessionSerializer, self).to_representation(instance)
        data['start_time_utc'] = format_date_for_display(data['start_time_utc'])
        data['total_elapsed_time'] = format_timespan_for_display(data['total_elapsed_time'])
        data['total_distance'] = format_distance_for_display(data['total_distance'])
        data['start_location'] = convert_lat_long_to_location_name(data['start_position_lat_deg'], data['start_position_long_deg'])
        return data

    class Meta:
        model = ActivityWalkSession
        fields = [
            'start_time_utc',
            'start_position_lat_deg',
            'start_position_long_deg',
            'total_elapsed_time',
            'total_distance',
            'total_strides',
            'total_calories',
        ]


class ActivityWalkFileSerializer(serializers.ModelSerializer):
    activitywalkdata = ActivityWalkDataSerializer(many=True, read_only=True)
    activitywalksession = ActivityWalkSessionSerializer(many=True, read_only=True)

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
        ret = super(ActivityWalkFileSerializer, self).data
        # Filter out records that were recorded by the watch before GPS was enabled
        # TODO consider replacing the None with the starting coordinate if we need other data later
        ret['activitywalkdata'] = list(filter((None).__ne__, ret['activitywalkdata']))

        session_data = ret.pop('activitywalksession')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityWalkFile
        fields = ['activity_type', 'display_name', 'activitywalkdata', 'activitywalksession']


class ActivityWalkFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    def _get_activity_session_data(self, fit_file):
        session_data = [row for row in fit_file.get_messages('session')][0]
        return {
            'timestamp_utc': convert_ant_timestamp_to_unix_timestamp(session_data.get('timestamp').value),
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

    def validate(self, attrs):
        fit_file = FitFile(self.initial_data['file'])
        attrs['file'] = fit_file
        attrs['filename'] = self.initial_data['file'].split("/")[-1].split(".")[0]
        attrs['display_name'] = self.initial_data['display_name']
        attrs['session_data'] = self._get_activity_session_data(fit_file)
        return attrs

    def create(self, validated_data):
        newfiledata = None
        with transaction.atomic():
            walk_file = ActivityWalkFile(filename=validated_data['filename'], display_name=validated_data['display_name'])
            walk_file.save()

            walk_session = ActivityWalkSession(file=walk_file, **validated_data['session_data'])
            walk_session.save()

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

            for record in validated_data['file'].get_messages('record'):
                rowdict = {'file': walk_file}
                for record_data in record:
                    if record_data.name in generic_fields:
                        rowdict[record_data.name] = record_data.value
                    if record_data.name in time_fields:
                        rowdict[f'{record_data.name}_utc'] = convert_ant_timestamp_to_unix_timestamp(record_data.value)
                    if record_data.name in gps_fields:
                        rowdict[f'{record_data.name}_sem'] = record_data.value
                        rowdict[f'{record_data.name}_deg'] = convert_semicircles_to_degrees(record_data.value)

                newfiledata = ActivityWalkData(**rowdict)
                newfiledata.save()

        return newfiledata

    class Meta:
        model = ActivityWalkData


class ActivityYogaFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    def validate(self, attrs):
        file_path = self.initial_data.get('file')
        if not file_path:
            raise ValidationError({"file": "File must be provided"})

        fit_file = FitFile(file_path)

        # determine activity type
        sport_data = [r for r in fit_file.get_messages('sport') if r.type == 'data'][0]
        sport = sport_data.get("sport")  # raw_value == 10 and value == training
        sub_sport = sport_data.get("sub_sport")


        attrs['file'] = fit_file
        attrs['filename'] = file_path.split("/")[-1].split(".")[0]
        attrs['display_name'] = self.initial_data['display_name']
        attrs['sport_name'] = sport.value
        attrs['sport_val'] = sport.raw_value
        attrs['sub_sport_name'] = sub_sport.value
        attrs['sub_sport_val'] = sub_sport.raw_value
        return attrs

    def create(self, validated_data):
        newfiledata = None
        with transaction.atomic():
            newfile = ActivityWalkFile(filename=validated_data['filename'], display_name=validated_data['display_name'])
            newfile.save()

            # reader = csv.reader(validated_data['file'])

            # TODO someday consider converting this to using ANT's file ids and field specifications
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

            for record in validated_data['file'].get_messages('record'):
                rowdict = {'file': newfile}
                for record_data in record:
                    if record_data.name in generic_fields:
                        rowdict[record_data.name] = record_data.value
                    if record_data.name in time_fields:
                        rowdict[f'{record_data.name}_utc'] = convert_ant_timestamp_to_unix_timestamp(record_data.value)
                    if record_data.name in gps_fields:
                        rowdict[f'{record_data.name}_sem'] = record_data.value
                        rowdict[f'{record_data.name}_deg'] = convert_semicircles_to_degrees(record_data.value)

                newfiledata = ActivityWalkData(**rowdict)
                newfiledata.save()

        return newfiledata

    class Meta:
        model = ActivityWalkData
