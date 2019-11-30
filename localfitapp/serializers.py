import csv
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import GVAMonitorFile, GVAMonitorStressData

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.utils.serializer_helpers import ReturnList


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
                "y": value.stress_level_value
            } for value in stress_data
        ]

    @property
    def data(self):
        stress_data = self._format_for_chart_js(self.initial_data)
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


class GVAMonitorFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    def _fix_watch_date(self, timestamp_str):
        # my watch is 20 years behind. oops.
        now = datetime.utcnow()
        timestamp = int(timestamp_str)
        watch_date_utc = datetime.fromtimestamp(timestamp, pytz.UTC)

        year_difference = now.year - watch_date_utc.year
        if year_difference:
            watch_date_utc = watch_date_utc + relativedelta(years=year_difference)
        return watch_date_utc

    def create(self, validated_data):
        if 'file' not in self.initial_data:
            raise ParseError("Empty content")

        f = self.initial_data['file']

        newfiledata = None
        ifile = open(f, "r", encoding="utf8")
        with transaction.atomic():
            newfile = GVAMonitorFile(filename=ifile.name)
            newfile.save()
            reader = csv.reader(ifile)
            for row in reader:
                # stress data
                # TODO bulk upload
                if row[0] == "Data" and row[2] == "stress_level":
                    newfiledata = GVAMonitorStressData(
                        file=newfile,
                        stress_level_time=self._fix_watch_date(row[4]),
                        stress_level_value=row[7],
                    )
                    newfiledata.save()

        return newfiledata

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = GVAMonitorStressData
