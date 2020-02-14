# 3rd Party
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from fitparse import FitFile

# Internal
from .models import TotalsFile


class ActivityTotalsFileUploadSerializer(serializers.Serializer):

    def validate(self, attrs):
        try:
            fit_file = FitFile(self.initial_data['file'])
        except FileNotFoundError:
            raise ValidationError({"file": "File does not exist"})
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

                    total_file, _ = TotalsFile.objects.get_or_create(sport=rowdict['sport'])
                    for (key, value) in rowdict.items():
                        setattr(total_file, key, value)
                    total_file.save()

                except Exception as e:
                    raise ValidationError("Failed to save file")

        return total_file

    class Meta:
        model = TotalsFile
