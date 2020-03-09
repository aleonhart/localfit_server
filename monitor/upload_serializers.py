# stdlib
from datetime import datetime, timezone

# 3rd Party
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST
import pytz

# Internal
from .models import MonitorFile, StressData, HeartRateData, RestingMetRateData, StepData
from localfitserver.utils import bitswap_ant_timestamp_to_unix_timestamp
from localfitserver import settings


class MonitorFileUploadSerializer(serializers.Serializer):
    parser_class = (FileUploadParser,)

    stress_fields = [
        'stress_level_value'
    ]

    stress_time_fields = [
        'stress_level_time'
    ]

    time_fields = [
        'timestamp'
    ]

    time_16_fields = [
        'timestamp_16'
    ]

    def _get_stress_data(self, fit_file, monitor_file):
        stress_obj = None
        for row in fit_file.get_messages('stress_level'):
            stress_data = {'file': monitor_file}
            for col in row:
                if col.name in self.stress_fields:
                    stress_data[col.name] = col.value
                if col.name in self.stress_time_fields:
                    stress_data[f'{col.name}_utc'] = timezone.make_aware(col.value, timezone=pytz.UTC)

            stress_obj = StressData(**stress_data)
            stress_obj.save()

        return stress_obj

    def _get_heart_rate_data(self, fit_file, monitor_file):
        heart_rate_obj = None
        most_recent_timestamp_ant_epoch = None

        for row in fit_file.get_messages('monitoring'):
            heart_rate_data = {'file': monitor_file}
            for col in row:
                if col.name == 'heart_rate':
                    heart_rate_data[col.name] = col.value
                if col.name in self.time_fields:
                    heart_rate_data[f'{col.name}_utc'] = timezone.make_aware(col.value, timezone=pytz.UTC)
                    most_recent_timestamp_ant_epoch = col.raw_value
                if col.name in self.time_16_fields:
                    timestamp = bitswap_ant_timestamp_to_unix_timestamp(most_recent_timestamp_ant_epoch, col.raw_value)
                    heart_rate_data['timestamp_utc'] = timestamp

            # throw out the rows without heart rate data
            if heart_rate_data.get('heart_rate'):
                heart_rate_obj = HeartRateData(**heart_rate_data)
                heart_rate_obj.save()

        return heart_rate_obj

    def _get_resting_metabolic_rate_data(self, fit_file, monitor_file):
        resting_metabolic_rate_obj = None
        for row in fit_file.get_messages('monitoring_info'):
            resting_metabolic_rate_data = {'file': monitor_file}
            for col in row:
                if col.name == 'resting_metabolic_rate':
                    resting_metabolic_rate_data[col.name] = col.value
                if col.name in self.time_fields:
                    resting_metabolic_rate_data[f'{col.name}_utc'] = timezone.make_aware(col.value, timezone=pytz.UTC)

            resting_metabolic_rate_obj = RestingMetRateData(**resting_metabolic_rate_data)
            resting_metabolic_rate_obj.save()

        return resting_metabolic_rate_obj

    def _get_step_data(self, fit_file, monitor_file):
        step_data = {'file': monitor_file}
        for row in fit_file.get_messages('monitoring'):
            for col in row:
                if col.name in self.time_fields:
                    if not step_data.get('date'):
                        # normally save dates in DB in UTC
                        # but since this is just a date value, needs to be local to get the right day
                        step_data['date'] = timezone.make_aware(col.value, timezone=pytz.timezone(settings.TIME_ZONE)).date()
                if col.name in ['steps']:
                    step_data[col.name] = col.value

        step_data_obj, _ = StepData.objects.get_or_create(
            date=step_data['date'],
        )

        step_data_obj.steps = step_data_obj.steps + step_data['steps'] if step_data_obj.steps else step_data['steps']
        step_data_obj.save()
        return step_data_obj

    def _validate_filename(self, filename):
        if MonitorFile.objects.filter(filename=filename).exists():
            raise ValidationError(detail={"file": "This file has already been uploaded."}, code=HTTP_400_BAD_REQUEST)

    def validate(self, attrs):
        attrs['fit_file'] = self.initial_data['fit_file']
        attrs['filename'] = self.initial_data['file'].name.split(".")[0]
        self._validate_filename(attrs['filename'])
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            file = MonitorFile(filename=validated_data['filename'])
            file.save()

            step = self._get_step_data(validated_data['fit_file'], file)
            stress = self._get_stress_data(validated_data['fit_file'], file)
            heart_rate = self._get_heart_rate_data(validated_data['fit_file'], file)
            resting_metabolic_rate = self._get_resting_metabolic_rate_data(validated_data['fit_file'], file)
        return resting_metabolic_rate

    class Meta:
        model = RestingMetRateData
