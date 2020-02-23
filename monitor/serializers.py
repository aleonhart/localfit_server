# 3rd Party
from django.utils import timezone
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

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


class PieChartListSerializer(serializers.ListSerializer):
    """
    Range: 0 to 100,
    0 to 25: REST
    26 to 50: LOW
    51 to 75: MED
    76 to 100: HIGH
    """

    def _format_for_pie_chart(self, data):
        return [
            {
                "date": "2020-01-01",
                "stress_data": {
                    "REST": 10,
                    "LOW": 20,
                    "MED": 30,
                    "HIGH": 40
                }
            },
            {
                "date": "2020-01-02",
                "stress_data": {
                    "REST": 10,
                    "LOW": 20,
                    "MED": 30,
                    "HIGH": 40
                }
            },
            {
                "date": "2020-01-03",
                "stress_data": {
                    "REST": 10,
                    "LOW": 20,
                    "MED": 30,
                    "HIGH": 40
                }
            },
            {
                "date": "2020-01-04",
                "stress_data": {
                    "REST": 10,
                    "LOW": 20,
                    "MED": 30,
                    "HIGH": 40
                }
            },
            {
                "date": "2020-01-05",
                "stress_data": {
                    "REST": 10,
                    "LOW": 20,
                    "MED": 30,
                    "HIGH": 40
                }
            },
        ]

    @property
    def data(self):
        data = self._format_for_pie_chart(self.instance)
        response = {
            # 'start_time': timezone.localtime(data[0]['t']) if data else [],
            # 'end_time': timezone.localtime(data[-1]['t']) if data else [],
            'stress': data
        }
        return ReturnDict(response, serializer=self)


class PieChartSerializer(serializers.Serializer):

    class Meta:
        list_serializer_class = PieChartListSerializer
