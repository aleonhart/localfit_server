# 3rd Party
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

# Internal
from .models import ActivityFile, Session, ActivityData
from localfitserver.utils import (
    format_timespan_for_display,
    format_distance_for_display,
    format_date_for_display,
    format_data_for_google_maps_api)


class BaseActivityListSerializer(serializers.ListSerializer):
    chart_field = None

    def _format_for_chart_js(self, data, field):
        return [
            {
                "t": value.timestamp_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "y": getattr(value, field) if getattr(value, field) != -1 else 0
            } for value in data
        ]

    @property
    def data(self):
        data = self._format_for_chart_js(self.instance, self.chart_field)
        response = {
            'start_time': data[0]['t'] if data else [],
            'end_time': data[-1]['t'] if data else [],
            self.chart_field: data
        }
        return ReturnDict(response, serializer=self)


class ActivityHeartRateListSerializer(BaseActivityListSerializer):
    chart_field = 'heart_rate'


class ActivityHeartRateSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        super(ActivityHeartRateSerializer, self).to_representation(instance)
        return instance

    class Meta:
        model = ActivityData
        list_serializer_class = ActivityHeartRateListSerializer
        fields = ['timestamp_utc', 'heart_rate']


class ActivityAltitudeListSerializer(BaseActivityListSerializer):
    chart_field = 'altitude'


class ActivityAltitudeSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        super(ActivityAltitudeSerializer, self).to_representation(instance)
        return instance

    class Meta:
        model = ActivityData
        list_serializer_class = ActivityAltitudeListSerializer
        fields = ['timestamp_utc', 'altitude', 'enhanced_altitude']


class ActivityMapDataListSerializer(serializers.ListSerializer):
    @property
    def data(self):
        ret = super(ActivityMapDataListSerializer, self).data
        # Filter out records that were recorded by the watch before GPS was established
        ret = list(filter((None).__ne__, ret))
        return ReturnList(ret, serializer=self)


class ActivityMapDataSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super(ActivityMapDataSerializer, self).to_representation(instance)
        return format_data_for_google_maps_api(data['position_lat_deg'], data['position_long_deg'])

    class Meta:
        model = ActivityData
        list_serializer_class = ActivityMapDataListSerializer
        fields = ['position_lat_deg', 'position_long_deg']


class ActivityWalkDataSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super(ActivityWalkDataSerializer, self).to_representation(instance)
        if data['position_lat_deg'] and data['position_long_deg']:
            return {'lat': data['position_lat_deg'], 'lng': data['position_long_deg']} \
                if data['position_lat_deg'] and data['position_long_deg'] else None

    class Meta:
        model = ActivityData
        fields = ['position_lat_deg', 'position_long_deg']


class ActivityWalkSessionSerializer(serializers.ModelSerializer):
    total_distance = serializers.DecimalField(max_digits=8, decimal_places=2)

    def to_representation(self, instance):
        data = super(ActivityWalkSessionSerializer, self).to_representation(instance)
        data['start_time_utc_dt'] = data['start_time_utc']
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


class ActivityMetaDataSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    @property
    def data(self):
        ret = super().data
        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        fields = ['activity_type', 'start_time_utc', 'session']


class ActivitiesListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        files = super(ActivitiesListSerializer, self).data
        for file in files:
            session_data = file.pop('session')[0]
            file.update(**session_data)
        return ReturnList(files, serializer=self)


class ActivitiesSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)

    class Meta:
        model = ActivityFile
        list_serializer_class = ActivitiesListSerializer
        fields = ['filename', 'activity_type', 'activity_category', 'start_time_utc', 'session']


class ActivityWalkFileListSerializer(serializers.ListSerializer):

    @property
    def data(self):
        files = super(ActivityWalkFileListSerializer, self).data
        for file in files:
            session_data = file.pop('session')[0]
            file.pop('activitydata')  # TODO dont get this data from the DB in the first place
            file.update(**session_data)
        # TODO any way to avoid this or get it into the query?
        sorted_files = sorted(files, key=lambda f: f['start_time_utc_dt'], reverse=True)
        return ReturnList(sorted_files, serializer=self)


class ActivityWalkFileSerializer(serializers.ModelSerializer):
    session = ActivityWalkSessionSerializer(many=True, read_only=True)
    activitydata = ActivityWalkDataSerializer(many=True, read_only=True)

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
        ret['activitydata'] = list(filter((None).__ne__, ret['activitydata']))

        session_data = ret.pop('session')[0]
        ret.update(**session_data)
        return ReturnDict(ret, serializer=self)

    class Meta:
        model = ActivityFile
        list_serializer_class = ActivityWalkFileListSerializer
        fields = ['activity_type', 'activity_category', 'filename', 'session', 'activitydata']
