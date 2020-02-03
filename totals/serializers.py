# 3rd Party
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

# Internal
from .models import TotalsFile
from localfitserver.utils import format_distance_for_display, format_duration_for_display


class TotalsListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        ret = super().data
        return ReturnList(ret, serializer=self)


class TotalsSerializer(serializers.ModelSerializer):

    @property
    def data(self):
        ret = super().data
        return ReturnDict(ret, serializer=self)

    def to_representation(self, instance):
        data = super(TotalsSerializer, self).to_representation(instance)
        data['timer_time'] = format_duration_for_display(data['timer_time']) if data.get('timer_time') else None
        data['distance'] = format_distance_for_display(data['distance'], decimals=0) if data.get('distance') else None
        data['calories'] = f"{data['calories']:,}"
        return data

    class Meta:
        model = TotalsFile
        list_serializer_class = TotalsListSerializer

        fields = ['timer_time', 'distance', 'calories']
