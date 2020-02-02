# STDLIB
import csv

# 3rd Party
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
from fitparse import FitFile

import pytz
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from rest_framework.exceptions import ValidationError


# Internal
from .models import MonitorStressFile, MonitorStressData, MonitorHeartRateData
from localfitserver.utils import convert_ant_timestamp_to_unix_timestamp, bitswap_ant_timestamp_to_unix_timestamp


class BaseListSerializer(serializers.ListSerializer):
    chart_field = None

    def _format_for_chart_js(self, data, field):
        return [
            {
                "t": value.timestamp_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "y": getattr(value, field) if getattr(value, field) != -1 else 0
            } for value in data
        ]

    @property
    def data(self):
        data = self._format_for_chart_js(self.instance, self.chart_field)
        response = {
            'start_time': data[0]['t'] if data else [],
            'end_time': data[-1]['t'] if data else [],
            self.chart_field: data
        }
        return ReturnDict(response, serializer=self)


class HeartRateDataListSerializer(BaseListSerializer):
    chart_field = 'heart_rate'


class HeartRateDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonitorHeartRateData
        list_serializer_class = HeartRateDataListSerializer
        fields = ['timestamp_utc', 'heart_rate']


class StressDataListSerializer(serializers.ListSerializer):
    """
    ChartJS format
    [
      {
        t: "2019-10-26 07:01:00",
        y: 60
      },
    ]
    """

    def _format_for_chart_js(self, data):
        return [
            {
                "t": value.stress_level_time.strftime("%Y-%m-%d %H:%M:%S"),
                "y": value.stress_level_value if value.stress_level_value != -1 else 0
            } for value in data
        ]

    @property
    def data(self):
        data = self._format_for_chart_js(self.instance)
        return ReturnList(data, serializer=self)


class StressDataSerializer(serializers.Serializer):

    class Meta:
        list_serializer_class = StressDataListSerializer


"""

Monitor File
- heart rate data
Field 0 = Data
Field 2 = monitoring

Local Number
0 => ?
2 => START HERE. heart rate values.
Field 3="timestamp_16"
Field 4=timestamp
Field 5=units "s"
Field 6="heart_rate"
Field 7=heart rate value
Field 8=units "bpm"

4=>
Field 3=timestamp
Field 4=
Field 5=
Field 6=
Field 7=
Field 8=

4=>
Field 3=cycles OR steps
Field 4=value
Field 5=units "cycles"
Field 6="active_time"
Field 7=value (bigger, 100s)
Field 8=units "s"
Field 9="active_calories"
Field 10=value (10)
Field 11=units "kcal"
Field 12="timestamp_16"
Field 13=value
Field 14=units "s"
Field 15="current_activity_type_intensity"
Field 16=value (160)
Field 17=units
Field 18=activity_type
Field 19=value (0 for cycles)
Field 20=units
Field 21="intensity"
Field 22=value (1,2,3)
Field 23=units

5=>
timestamp

6=>
more cycle/steps. rollups?

7=> THEN HERE. activity and intensity levels
Field 3="timestamp"
Field 4=value
Field 5=units "s"
Field 6="current_activity_type_intensity"
Field 7=value (hundreds)
Field 8=units
Field 9="activity_type"
Field 10= 1 or 8 or none
Field 11=units
Field 12="intensity"
Field 13=value
Field 14=units


"""


class MonitorHeartRateFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    generic_fields = [
        'heart_rate'
    ]
    time_fields = [
        'timestamp'
    ]
    time_16_fields = [
        'timestamp_16'
    ]

    def validate(self, attrs):
        if not self.initial_data.get('file'):
            raise ValidationError({"file": "File must be provided"})

        fit_file = FitFile(self.initial_data['file'])
        attrs['file'] = fit_file
        attrs['filename'] = self.initial_data['file'].split("/")[-1].split(".")[0]
        return attrs

    def create(self, validated_data):
        newfiledata = None
        most_recent_timestamp_ant_epoch = None

        with transaction.atomic():
            file = MonitorStressFile(filename=validated_data['filename'])
            file.save()

            for row in validated_data['file'].get_messages('monitoring'):
                data = {'file': file}
                for col in row:
                    if col.name in self.generic_fields:
                        data[col.name] = col.value
                    if col.name in self.time_fields:
                        data[f'{col.name}_utc'] = convert_ant_timestamp_to_unix_timestamp(col.value)
                        most_recent_timestamp_ant_epoch = col.raw_value
                    if col.name in self.time_16_fields:
                        timestamp = bitswap_ant_timestamp_to_unix_timestamp(most_recent_timestamp_ant_epoch, col.raw_value)
                        data['timestamp_utc'] = timestamp

                # throw out the rows without heart rate data
                if data.get('heart_rate'):
                    newfiledata = self.Meta.model(**data)
                    newfiledata.save()

        return newfiledata

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = MonitorHeartRateData
