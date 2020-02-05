# 3rd Party
from rest_framework import serializers

# Internal
from .models import HeartRateData, RestingMetRateData
from localfitserver.base_serializers import BaseChartJSListSerializer


class RestingMetaRateListSerializer(BaseChartJSListSerializer):
    chart_field = 'resting_metabolic_rate'


class RestingMetaRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RestingMetRateData
        list_serializer_class = RestingMetaRateListSerializer
        fields = ['timestamp_utc', 'resting_metabolic_rate']


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
