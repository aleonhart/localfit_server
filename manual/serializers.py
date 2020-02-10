# stdlib

# 3rd Party
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

# Internal
from .models import ManualStats
from localfitserver.utils import get_vo2_max_range


class Vo2MaxSerializer(serializers.ModelSerializer):

    @property
    def data(self):
        ret = super().data
        ret['vo2_range'] = get_vo2_max_range(ret['vo2_max'])
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ManualStats
        fields = ['vo2_max']
