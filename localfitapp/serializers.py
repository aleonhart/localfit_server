import csv

from .models import GVAMonitorData, GVAMonitorFile

from django.db import transaction
from rest_framework import serializers
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response


class GVAMonitorDataSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = GVAMonitorData


class GVAMonitorFileUploadSerializer(serializers.Serializer):

    def create(self, validated_data):
        file = validated_data['file']
        with transaction.atomic():
            with open(file) as f:
                reader = csv.reader(f)
                for row in reader:
                    newfile = GVAMonitorFile(filename=file.name)
                    newfile.save()

                    newfiledata = GVAMonitorData(
                        file=newfile,
                        type=row[0],
                        local_number=row[0],
                        message=row[1],
                        field_1=row[2],
                        value_1=row[3],
                        units_1=row[4],
                        field_2=row[5],
                        value_2=row[6],
                        units_2=row[7],
                        field_3=row[8],
                        value_3=row[9],
                        units_3=row[10],
                        field_4=row[11],
                        value_4=row[12],
                        units_4=row[13],
                        field_5=row[14],
                        value_5=row[15],
                        units_5=row[16],
                        field_6=row[17],
                        value_6=row[18],
                        units_6=row[19],
                        field_7=row[20],
                        value_7=row[21],
                        units_7=row[22],
                        field_8=row[23],
                        value_8=row[24],
                        units_8=row[25],
                    )
                    newfiledata.save()

        return newfiledata

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = GVAMonitorData
