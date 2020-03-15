# stdlib
from datetime import datetime, time
from decimal import Decimal

# 3rd Party
from django.db.models.functions.datetime import TruncDate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

# Internal
from .models import HeartRateData, RestingMetRateData, StepData
from localfitserver.base_serializers import BaseChartJSListSerializer


class StepDataListSerializer(BaseChartJSListSerializer):
    chart_field = 'steps'
    time_field = 'date'

    def _format_for_chart_js(self, data):
        return [
            {
                "t": getattr(value, self.time_field).strftime("%Y-%m-%d"),
                "y": getattr(value, self.chart_field) if getattr(value, self.chart_field) != -1 else 0
            } for value in data.order_by('date')
        ]


class StepDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = StepData
        list_serializer_class = StepDataListSerializer
        fields = ['date', 'steps']


class StepGoalListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        actual_total_steps = sum(self.instance.values_list('steps', flat=True))
        goal_total_steps = 5000 * self.context["days_in_month"]
        response = {
            'monthly_step_goal_percent_completed': round((actual_total_steps / goal_total_steps) * 100)
        }
        return ReturnDict(response, serializer=self)


class StepGoalSerializer(serializers.ModelSerializer):

    class Meta:
        model = StepData
        list_serializer_class = StepGoalListSerializer
        fields = ['date', 'steps']


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

    def _get_range_by_value(self, value):
        range = "NONE"
        if 0 <= value <= 25:
            range = "REST"
        if 25 < value <= 50:
            range = "LOW"
        if 50 < value <= 75:
            range = "MED"
        if 75 < value <= 100:
            range = "HIGH"

        return range

    def _build_stress_payload(self, data, date_range):
        stress_ranges = [
            self._get_range_by_value(d.stress_level_value) for d in
            data.filter(**date_range)
        ]
        rest = stress_ranges.count("REST")
        low = stress_ranges.count("LOW")
        med = stress_ranges.count("MED")
        high = stress_ranges.count("HIGH")
        actual_stress_data_range = rest + low + med + high
        return {
            "date": date_range['stress_level_time_utc__range'][0].date(),
            "stress_data": {
                "REST": round(Decimal((rest / actual_stress_data_range) * 100), 0),
                "LOW": round(Decimal((low / actual_stress_data_range) * 100), 0),
                "MED": round(Decimal((med / actual_stress_data_range) * 100), 0),
                "HIGH": round(Decimal((high / actual_stress_data_range) * 100), 0)
            }
        }

    def _format_for_pie_chart(self, data):
        stress_response = []
        stress_dates = [
            d['date'] for d in
            data.annotate(date=TruncDate('stress_level_time_utc')).values('date').distinct()
        ]
        for stress_date in stress_dates:
            date_range = {
                'stress_level_time_utc__range': (
                datetime.combine(stress_date, time.min), datetime.combine(stress_date, time.max))
            }
            stress_payload = self._build_stress_payload(data, date_range)
            stress_response.append(stress_payload)
        return stress_dates, stress_response

    @property
    def data(self):
        stress_dates, stress_response = self._format_for_pie_chart(self.instance)
        response = {
            'start_date': stress_dates[0],
            'end_date': stress_dates[-1],
            'stress': stress_response
        }
        return ReturnDict(response, serializer=self)


class PieChartSerializer(serializers.Serializer):

    class Meta:
        list_serializer_class = PieChartListSerializer
