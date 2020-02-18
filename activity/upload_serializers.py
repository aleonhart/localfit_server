# 3rd Party
from django.db import transaction
from django.utils.timezone import make_aware
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
import pytz

# Internal
from .models import ActivityFile, Session, ActivityData
from localfitserver.utils import (
    convert_semicircles_to_degrees,
    convert_lat_long_to_location_name)


class BaseActivityFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    generic_fields = []
    time_fields = []
    gps_fields = []

    def _save_activity_file(self, filename, start_time_utc):
        raise ValidationError("Child class must implement this method!")

    def _get_activity_session_data(self, fit_file):
        session_data = [row for row in fit_file.get_messages('session')][0]
        formatted_session_data = {
            'start_time_utc': make_aware(session_data.get('start_time').value, timezone=pytz.UTC),
            'total_elapsed_time': session_data.get('total_elapsed_time').value,
            'total_timer_time': session_data.get('total_timer_time').value,
            'total_distance': session_data.get('total_distance').value,
            'total_strides': session_data.get('total_strides').value if session_data.get('total_strides') else None,
            'total_cycles': session_data.get('total_cycles').value if session_data.get('total_cycles') else None,
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

        # GPS data only present when GPS is enabled and relevant to the activity
        if session_data.get('start_position_lat').value and session_data.get('start_position_long').value:
            start_position_lat_deg = convert_semicircles_to_degrees(session_data.get('start_position_lat').value)
            start_position_long_deg = convert_semicircles_to_degrees(session_data.get('start_position_long').value)
            formatted_session_data.update({
                'start_position_lat_sem': session_data.get('start_position_lat').value,
                'start_position_long_sem': session_data.get('start_position_long').value,
                'start_position_lat_deg': start_position_lat_deg,
                'start_position_long_deg': start_position_long_deg,
                'start_location': convert_lat_long_to_location_name(start_position_lat_deg, start_position_long_deg),
            })

        return formatted_session_data

    def validate(self, attrs):
        attrs['fit_file'] = self.initial_data['fit_file']
        attrs['filename'] = self.initial_data['file'].name.split(".")[0]
        attrs['session_data'] = self._get_activity_session_data(self.initial_data['fit_file'])
        return attrs

    def create(self, validated_data):
        newfiledata = None
        with transaction.atomic():
            try:
                file = self._save_activity_file(validated_data['filename'], validated_data['session_data']['start_time_utc'])
            except Exception as e:
                raise ValidationError(e)

            try:
                session = Session(file=file, **validated_data['session_data'])
                session.save()
            except Exception as e:
                raise ValidationError("Failed to save file session data")

            for record in validated_data['fit_file'].get_messages('record'):
                rowdict = {'file': file}
                for record_data in record:
                    if record_data.name in self.generic_fields:
                        rowdict[record_data.name] = record_data.value
                    if record_data.name in self.time_fields:
                        rowdict[f'{record_data.name}_utc'] = make_aware(record_data.value, timezone=pytz.UTC)
                    if record_data.name in self.gps_fields:
                        rowdict[f'{record_data.name}_sem'] = record_data.value
                        rowdict[f'{record_data.name}_deg'] = convert_semicircles_to_degrees(record_data.value)

                newfiledata = self.Meta.model(**rowdict)
                newfiledata.save()

        return newfiledata

    class Meta:
        model = None


class ActivityWalkFileUploadSerializer(BaseActivityFileUploadSerializer):
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

    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='walk',
                            activity_category='recorded')
        file.save()
        return file

    class Meta:
        model = ActivityData


class ActivityRunFileUploadSerializer(ActivityWalkFileUploadSerializer):

    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='run',
                            activity_category='recorded')
        file.save()
        return file


class ActivityTreadmillFileUploadSerializer(ActivityWalkFileUploadSerializer):

    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='treadmill',
                            activity_category='recorded')
        file.save()
        return file

    class Meta:
        model = ActivityData


class ActivityEllipticalFileUploadSerializer(ActivityWalkFileUploadSerializer):

    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='elliptical',
                            activity_category='recorded')
        file.save()
        return file

    class Meta:
        model = ActivityData


class ActivityYogaFileUploadSerializer(BaseActivityFileUploadSerializer):
    generic_fields = [
        'heart_rate',
    ]
    time_fields = [
        'timestamp'
    ]

    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='yoga',
                            activity_category='recorded')
        file.save()
        return file

    class Meta:
        model = ActivityData


class ActivityStairClimbingFileUploadSerializer(ActivityYogaFileUploadSerializer):
    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='stairmaster',
                            activity_category='recorded')
        file.save()
        return file


class ActivityCardioFileUploadSerializer(ActivityYogaFileUploadSerializer):
    def _save_activity_file(self, filename, start_time_utc):
        file = ActivityFile(filename=filename,
                            start_time_utc=start_time_utc,
                            activity_type='beat_saber',
                            activity_category='recorded')
        file.save()
        return file
