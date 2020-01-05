# STDLIB
import csv

# 3rd Party
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
import pytz
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.utils.serializer_helpers import ReturnList
from rest_framework.exceptions import ValidationError


# Internal
from .models import MonitorStressFile, MonitorStressData
from localfitserver.utils import convert_ant_timestamp_to_unix_timestamp


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

    def _format_for_chart_js(self, stress_data):
        return [
            {
                "t": value.stress_level_time.strftime("%Y-%m-%d %H:%M:%S"),
                "y": value.stress_level_value if value.stress_level_value != -1 else 0
            } for value in stress_data
        ]

    @property
    def data(self):
        stress_data = self._format_for_chart_js(self.instance)
        return ReturnList(stress_data, serializer=self)


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


class MonitorStressFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    def validate(self, attrs):
        if not self.initial_data.get('file'):
            raise ValidationError({"file": "File must be provided"})

        try:
            open_file = open(self.initial_data['file'], "r", encoding="utf8")
        except FileNotFoundError:
            raise ValidationError({"file": "File not found"})
        attrs['file'] = open_file
        return attrs

    def create(self, validated_data):

        with transaction.atomic():
            filename = validated_data['file'].name.split("/")[-1].split(".")[0]
            newfile = MonitorStressFile(filename=filename)
            newfile.save()

            reader = csv.reader(validated_data['file'])
            for row in reader:
                # stress data
                # TODO bulk upload
                if row[0] == "Data" and row[2] == "stress_level":
                    newfiledata = MonitorStressData(
                        file=newfile,
                        stress_level_time=convert_ant_timestamp_to_unix_timestamp(row[4]),
                        stress_level_value=row[7],
                    )
                    newfiledata.save()

        return newfiledata

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = MonitorStressData