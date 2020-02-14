# 3rd Party
from fitparse import FitFile, FitParseError

from django.utils import timezone
from rest_framework import serializers
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ValidationError
import pytz

# Internal
from .models import MonitorFile, StressData, HeartRateData, RestingMetRateData
from localfitserver.utils import bitswap_ant_timestamp_to_unix_timestamp


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

        # TODO distance (decimal m), steps, active_time (s), active_calories, duration_min, activity_type (int)
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
        step_obj = None
        step_data = {'file': monitor_file}
        for row in fit_file.get_messages('monitoring'):
            for col in row:
                if col.name in ['steps', 'active_calories']:
                    step_data[col.name] = col.value

        return step_obj

    def validate(self, attrs):
        if not self.initial_data.get('file'):
            raise ValidationError({"file": "File must be provided"})

        try:
            fit_file = FitFile(self.initial_data['file'])
        except FileNotFoundError:
            raise ValidationError({"file": "File does not exist"})

        attrs['file'] = fit_file
        attrs['filename'] = self.initial_data['file'].split("/")[-1].split(".")[0]
        return attrs

    def create(self, validated_data):
        # with transaction.atomic():
        file = MonitorFile(filename=validated_data['filename'])
        file.save()

        step = self._get_step_data(validated_data['file'], file)
        stress = self._get_stress_data(validated_data['file'], file)
        heart_rate = self._get_heart_rate_data(validated_data['file'], file)
        resting_metabolic_rate = self._get_resting_metabolic_rate_data(validated_data['file'], file)
        return resting_metabolic_rate

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = RestingMetRateData
