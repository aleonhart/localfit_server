# 3rd Party
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

# Internal
from .models import ActivityFile, Session, WalkData
from localfitserver.utils import (
    format_timespan_for_display,
    format_distance_for_display,
    format_date_for_display)


class ActivityWalkDataSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super(ActivityWalkDataSerializer, self).to_representation(instance)
        if data['position_lat_deg'] and data['position_long_deg']:
            return {'lat': data['position_lat_deg'], 'lng': data['position_long_deg']} \
                if data['position_lat_deg'] and data['position_long_deg'] else None

    class Meta:
        model = WalkData
        fields = ['position_lat_deg', 'position_long_deg']


class ActivityWalkSessionSerializer(serializers.ModelSerializer):
    total_distance = serializers.DecimalField(max_digits=8, decimal_places=2)

    def to_representation(self, instance):
        data = super(ActivityWalkSessionSerializer, self).to_representation(instance)
        data['start_time_utc'] = format_date_for_display(data['start_time_utc']) if data.get('start_time_utc') else None
        data['total_elapsed_time'] = format_timespan_for_display(data['total_elapsed_time']) if data.get('total_elapsed_time') else None
        data['total_distance'] = format_distance_for_display(data['total_distance']) if data.get('total_distance') else None
        return data

    class Meta:
        model = Session
        fields = [
            'start_time_utc',
            'start_position_lat_deg',
            'start_position_long_deg',
            'start_location',
            'total_elapsed_time',
            'total_distance',
            'total_strides',
            'total_calories',
        ]


class ActivityWalkFileListSerializer(serializers.ListSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    @property
    def data(self):
        files = super(ActivityWalkFileListSerializer, self).data
        for file in files:
            session_data = file.pop('session')[0]
            file.pop('activitywalkdata')  # TODO dont get this data from the DB in the first place
            file.update(**session_data)
        return ReturnList(files, serializer=self)


class ActivityWalkFileSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)
    activitywalkdata = ActivityWalkDataSerializer(many=True, read_only=True)

    @property
    def data(self):
        """
        Front End expects this format for easy parsing by Google Maps API
        {
            data: {
                results: [
                    { lat: 41.365286, lng: -124.018488 },
                    { lat: 41.365236, lng: -124.018411 }
                ]
            }
        }
        """
        ret = super(ActivityWalkFileSerializer, self).data
        # Filter out records that were recorded by the watch before GPS was enabled
        # TODO consider replacing the None with the starting coordinate if we need other data later
        ret['activitywalkdata'] = list(filter((None).__ne__, ret['activitywalkdata']))

        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        list_serializer_class = ActivityWalkFileListSerializer
        fields = ['activity_type', 'filename', 'session', 'activitywalkdata']
