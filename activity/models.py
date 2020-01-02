from django.db import models


class ActivityWalkFile(models.Model):
    """
    Activity Walk files (ACTIVITY)
    """
    filename = models.CharField(max_length=15, unique=True)


class ActivityWalkData(models.Model):
    """
    FIT files store coordinates as semicircles.
    Semicircles allows for a standard 32 bit integer to represent 360 degrees.

    Google Maps API, which will be used to display the data,
    accepts coordinates according to the World Geodetic System WGS84
    (https://en.wikipedia.org/wiki/World_Geodetic_System) standard, as
    degrees.

    Latitude  range is -90  and +90  degrees respective to the Equator.
    Longitude range is -180 and +180 degrees respective to the Prime Meridian.

    180 degrees to 2^31 semicircles

    Example:
    Degrees = Semicircles*(180/2^31)
    41.364685 = 493499921*(180/2^31)

    .000001 decimal degree is approximately 0.1m (10cm).
    Google Maps resolution is approximately 1.0m.

    Store as degrees to save time on display conversion for GMAPI.
    """

    """
    Walk data from activity files (ACTIVITY).
    
    Fields in this file are in an unreliable order.
    This appears to be because the GPS does not attain signal immediately
    after the activity begins. Once GPS signal is obtained, GPS begins
    recording and is added to the file.

    Field 0="Data"
    Field 2="record"
    Field 3="timestamp"
    Field 4=timestamp
    Field 5=units "s"
    ---
    "position_lat" int (semicircles) <- convert to degrees for display
    "position_long" int (semicircles)
    ---
    "distance" float (m)
    "altitude" float (m)
    "speed" float (m/s)
    "heart_rate" integer (bpm)
    "cadence" integer (rpm)
    "fractional_cadence" float (rpm)
    "enhanced_altitude" float (m)
    "enhanced_speed" float (m/s)
    """
    activity_walk_data_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(ActivityWalkFile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()          # seconds
    position_lat_sem = models.IntegerField()    # semicircles
    position_long_sem = models.IntegerField()   # semicircles
    position_lat_deg = models.DecimalField(max_digits=8, decimal_places=6)   #  XX.XXXXXX degrees
    position_long_deg = models.DecimalField(max_digits=9, decimal_places=6)  # XXX.XXXXXX degrees
    distance = models.DecimalField(max_digits=8, decimal_places=2)           # meters, 100mi is 160,934m
    altitude = models.DecimalField(max_digits=5, decimal_places=1)           # meters, Mt. Everest is 8,850m high
    speed = models.DecimalField(max_digits=5, decimal_places=3)              # meters/second, Usain Bolt's top speed is 12.27m/s
    heart_rate = models.IntegerField()          # BPM
    cadence = models.IntegerField()             # RPM
    fractional_cadence = models.IntegerField()  # RPM
    enhanced_altitude = models.DecimalField(max_digits=5, decimal_places=1)  # meters
    enhanced_speed = models.DecimalField(max_digits=5, decimal_places=3)     # meters/second


