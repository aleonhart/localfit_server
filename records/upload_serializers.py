# 3rd Party
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from fitparse import FitFile

# Internal
from .models import RecordsFile


class RecordsFileUploadSerializer(serializers.Serializer):

    def validate(self, attrs):
        fit_file = FitFile(self.initial_data['file'])
        attrs['file'] = fit_file
        return attrs

    def create(self, validated_data):
        total_file = None
        with transaction.atomic():
            for total in validated_data['file'].get_messages('totals'):
                try:
                    rowdict = {
                        t.name: t.value for t in total.fields
                        if t.name in ['distance', 'calories', 'timer_time', 'sport']
                    }
                    # try:
                    #     total_file = TotalsFile.objects.get(sport=rowdict['sport'])
                    #     total_file(**rowdict)
                    # except TotalsFile.DoesNotExist as e:
                    #     total_file = TotalsFile(**rowdict)

                    # total_file.save()
                except Exception as e:
                    raise ValidationError("Failed to save file")

        return total_file

    class Meta:
        model = RecordsFile
