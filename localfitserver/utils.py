# 3rd Party
from datetime import timedelta, datetime
from decimal import Decimal
from geopy.geocoders import Nominatim


def convert_ant_timestamp_to_unix_timestamp(ant_timestamp):
    """
    ANT does not utilize the traditional UNIX epoch.
    ANT epoch: 1989-12-31 00:00:00 UTC
    UNIX epoch: 1970-01-01 00:00:00 UTC
    UNIX - ANT = 631065600 seconds
    """

    DIFF_ANT_EPOCH_UNIX_EPOC_MILLIS = 631065600
    unix_timestamp = ant_timestamp + timedelta(milliseconds=DIFF_ANT_EPOCH_UNIX_EPOC_MILLIS)
    return unix_timestamp


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


def convert_lat_long_to_location_name(lat, long):
    # TODO look this up on file upload and save it in the db
    # geolocator = Nominatim(user_agent="localfit")
    # address = geolocator.reverse(f"{round(lat, 6)}, {round(long, 6)}").raw['address']
    # return f"{address['path']}, {address['county']} {address['state']}, {address['country']}"
    return "Cathedral Trees Trail, Humboldt County California, United States of America"


def format_timespan_for_display(seconds):
    """
    ANT FIT files record timespans in seconds.
    Format this to HH:MM:SS for the front end to display
    """
    return str(timedelta(seconds=int(seconds)))


def format_distance_for_display(meters):
    """
    Sorry! I'm from the USA. I'm defaulting
    everything to miles.
    """

    return round(Decimal(meters * Decimal(0.000621371192)), 2)


def format_date_for_display(date):
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
    return date_obj.strftime("%A %H:%M%p, %B %w, %Y")

