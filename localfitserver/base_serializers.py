# 3rd Party
from django.utils import timezone
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict


class BaseChartJSListSerializer(serializers.ListSerializer):
    chart_field = None
    time_field = 'timestamp_utc'

    def _format_for_chart_js(self, data):
        return [
            {
                "t": timezone.localtime(getattr(value, self.time_field)),
                "y": getattr(value, self.chart_field) if getattr(value, self.chart_field) != -1 else 0
            } for value in data
        ]

    @property
    def data(self):
        data = self._format_for_chart_js(self.instance)
        response = {
            'start_time': timezone.localtime(data[0]['t']) if data else [],
            'end_time': timezone.localtime(data[-1]['t']) if data else [],
            self.chart_field: data
        }
        return ReturnDict(response, serializer=self)
