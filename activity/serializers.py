# STDLIB
import csv

# 3rd Party
from django.db import transaction
from rest_framework import serializers
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ValidationError

# Internal
from .models import ActivityWalkFile, ActivityWalkData
from localfitserver.utils import convert_ant_timestamp_to_unix_timestamp, convert_semicircles_to_degrees


class ActivityFileUploadSerializer(serializers.Serializer):
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

        newfiledata = None
        with transaction.atomic():
            filename = validated_data['file'].name.split("/")[-1].split(".")[0]
            newfile = ActivityWalkFile(filename=filename)
            newfile.save()

            reader = csv.reader(validated_data['file'])

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

            for row in reader:
                # TODO bulk upload
                # TODO parse the file based on activity type (currently assumes walk file)
                if row[0] == "Data" and row[2] == "record":
                    rowdict = {'file': newfile}
                    for i, col in enumerate(row, start=0):
                        if col in generic_fields:
                            rowdict[col] = row[i + 1]
                        if col in time_fields:
                            rowdict[f'{col}_utc'] = convert_ant_timestamp_to_unix_timestamp(row[i + 1])
                        if col in gps_fields:
                            rowdict[f'{col}_sem'] = row[i + 1]
                            rowdict[f'{col}_deg'] = convert_semicircles_to_degrees(row[i + 1])

                    newfiledata = ActivityWalkData(**rowdict)
                    newfiledata.save()

        return newfiledata

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = ActivityWalkData
