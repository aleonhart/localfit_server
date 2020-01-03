# 3rd Party
from datetime import datetime
import pytz


def convert_ant_timestamp_to_unix_timestamp(ant_timestamp_str):
    '''
    ANT does not utilize the traditional UNIX epoch.
    ANT epoch: 1989-12-31 00:00:00 UTC
    UNIX epoch: 1970-01-01 00:00:00 UTC
    UNIX - ANT = 631065600 seconds
    '''

    epoch_difference = int(631065600)
    unix_timestamp = int(ant_timestamp_str) + epoch_difference
    watch_date_utc = datetime.fromtimestamp(unix_timestamp, pytz.UTC)

    return watch_date_utc


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
    return int(semicircles) * (180/(2**31))
