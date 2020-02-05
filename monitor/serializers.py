# 3rd Party
from rest_framework import serializers

# Internal
from .models import HeartRateData
from localfitserver.base_serializers import BaseChartJSListSerializer


class HeartRateDataListSerializer(BaseChartJSListSerializer):
    chart_field = 'heart_rate'


class HeartRateDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = HeartRateData
        list_serializer_class = HeartRateDataListSerializer
        fields = ['timestamp_utc', 'heart_rate']


class StressDataListSerializer(BaseChartJSListSerializer):
    chart_field = 'stress_level_value'
    time_field = 'stress_level_time_utc'


class StressDataSerializer(serializers.Serializer):

    class Meta:
        list_serializer_class = StressDataListSerializer
