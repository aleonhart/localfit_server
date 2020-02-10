# 3rd Party
from datetime import timedelta, datetime
from django.utils.timezone import make_aware
from decimal import Decimal
from geopy.geocoders import Nominatim
import pytz


def bitswap_ant_timestamp_to_unix_timestamp(timestamp_32, timestamp_16):
    """
    To save space, FIT stores timestamps in two formats:
    timestamp: 32 bits, stored as seconds since ANT epoch
    timestamp_16: 16-bit "suffix" since last timestamp

    In order to convert a timestamp_16 16-bit suffix into a
    32-bit ANT timestamp, you must bitswap the last 16 bits.

    """
    DIFF_ANT_EPOCH_UNIX_EPOC_SECONDS = 631065600
    timestamp_32 += (timestamp_16 - (timestamp_32 & 0xFFFF)) & 0xFFFF
    ant_timestamp = datetime.fromtimestamp(timestamp_32, tz=pytz.UTC)
    unix_timestamp = ant_timestamp + timedelta(seconds=DIFF_ANT_EPOCH_UNIX_EPOC_SECONDS)
    return unix_timestamp


def convert_ant_timestamp_to_unix_timestamp(ant_timestamp_utc):
    """
    ANT does not utilize the traditional UNIX epoch.
    ANT epoch: 1989-12-31 00:00:00 UTC
    UNIX epoch: 1970-01-01 00:00:00 UTC
    UNIX - ANT = 631065600 seconds (~20 years)
    """

    DIFF_ANT_EPOCH_UNIX_EPOC_MILLIS = 631065600
    unix_timestamp_utc = make_aware(ant_timestamp_utc + timedelta(milliseconds=DIFF_ANT_EPOCH_UNIX_EPOC_MILLIS), timezone=pytz.UTC)
    return unix_timestamp_utc


def convert_semicircles_to_degrees(semicircles):
    """
    ANT FIT files store coordinates as semicircles. This
    allows for a standard 32 bit integer to represent 360
    degrees with high precision.

    Google Maps API, which will be used to display the data,
    accepts coordinates according to the World Geodetic System WGS84
    standard, as degrees.

    ANT is highly concerned with storage limits due to saving data on GPS watches.
    This (web)app is more concerned with browser-side rendering times. Therefor,
    it will convert semicircles to degrees before storing the data the DB to speed
    up the render of the maps in the browser.

    Precision:
    Latitude  range is -90  and +90  degrees respective to the Equator.
    Longitude range is -180 and +180 degrees respective to the Prime Meridian.

    .000001 decimal degree is approximately 0.1m (10cm).
    Google Maps resolution is approximately 1.0m.

    Storage with with 6 decimal point precision should more than suffice.

    Semicircle to Degrees Equation:
    180 degrees = 2^31 semicircles

    Example:
    Degrees = Semicircles*(180/2^31)
    41.364685 = 493499921*(180/2^31)
    """
    return round(semicircles * (180/(2**31)), 6)


def calculate_geographic_midpoint(list_of_coordinates):
        """
        Calculating a real geographic midpoint is complicated, but for
        distances as small as I will realistically be traveling by foot,
        it is reasonable to simplify and assume the shape the path forms is
        a 2D plane, which makes taking the average "good enough".

        Expected Parameter Format
        [{'lat': Decimal('00.000000'), 'lng': Decimal('000.000000')}]
        """
        lat = []
        long = []
        for coordinates in list_of_coordinates:
            lat.append(coordinates['lat'])
            long.append(coordinates['lng'])

        midpoint_lat_deg = sum(lat) / len(lat)
        midpoint_long_deg = sum(long) / len(long)
        return round(midpoint_lat_deg, 6), round(midpoint_long_deg, 6)


def convert_lat_long_to_location_name(lat, long):
    if lat and long:
        # TODO call to geolocator can fail and should be made async
        geolocator = Nominatim(user_agent="localfit")
        address = geolocator.reverse(f"{round(lat, 6)}, {round(long, 6)}").raw['address']
        small_location = address.get('path') or address.get('footway') or address.get('road') or address.get('street')
        med_location = address.get('hamlet') or address.get('village') or address.get('city')
        full_address = f"{small_location}, {med_location}, {address.get('county')}, {address.get('state')}"
    else:
        full_address = 'Unknown'
    return full_address


def format_timespan_for_display(seconds):
    """
    ANT FIT files record timespans in seconds.
    Format this to HH:MM:SS for the front end to display
    """
    return str(timedelta(seconds=int(seconds)))


def format_distance_for_display(meters, decimals=2):
    """
    Sorry! I'm from the USA. I'm defaulting
    everything to miles.

    Calculates meters to miles.
    """

    return round(Decimal(meters * Decimal(0.000621371192)), decimals)


def format_date_for_calendar_heat_map(datetime_obj):
    """
    Format: YYYY-MM-DD
    This is the format expected by https://github.com/kevinsqi/react-calendar-heatmap
    """
    return datetime_obj.strftime("%Y-%m-%d")


def format_date_for_display(date):
    """
    Format:
    04:10PM, Monday, December 30, 2019
    """
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
    return date_obj.strftime("%I:%M%p, %A, %B %d, %Y")


def format_duration_for_display(seconds):
    """
    Converts seconds to HH:MM:SS
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    # return f"{hours} hours, {minutes} minutes and {seconds} seconds"
    return hours


def format_data_for_google_maps_api(lat_degrees, long_degrees):
    """
    Formats a single WalkData record for Google Maps API.
    Meant to be called by serializer to_representation()

    Example:
    { lat: 41.365286, lng: -124.018488 }
    """
    return {'lat': lat_degrees, 'lng': long_degrees} if lat_degrees and long_degrees else None


def get_vo2_max_range(vo2_max):
    """
    For women age 30-39 (me)

    Superior    47.4
    Excellent   42.4
    Good        37.8
    Fair        34.4
    Poor       <34.4

    https://www8.garmin.com/manuals/webhelp/fenix3/EN-US/GUID-1FBCCD9E-19E1-4E4C-BD60-1793B5B97EB3.html
    """

    if vo2_max < 34.4:
        range = "Poor"
    elif 34.4 <= vo2_max < 37.8:
        range = "Fair"
    elif 37.8 <= vo2_max < 42.4:
        range = "Good"
    elif 42.4 <= vo2_max < 47.4:
        range = "Excellent"
    elif 47.4 <= vo2_max:
        range = "Superior"

    return range
