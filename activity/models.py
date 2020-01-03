from django.db import models


class ActivityWalkFile(models.Model):
    """
    Activity Walk files (ACTIVITY)
    """
    filename = models.CharField(max_length=15, unique=True)


class ActivityWalkData(models.Model):


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
    "position_lat" int (semicircles)
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
    timestamp_utc = models.DateTimeField()                                               # seconds
    position_lat_sem = models.IntegerField(null=True)                                    # semicircles
    position_long_sem = models.IntegerField(null=True)                                   # semicircles
    position_lat_deg = models.DecimalField(null=True, max_digits=8, decimal_places=6)    #      XX.XXXXXX degrees
    position_long_deg = models.DecimalField(null=True, max_digits=9, decimal_places=6)   #     XXX.XXXXXX degrees
    distance = models.DecimalField(max_digits=8, decimal_places=2)                       # XXX,XXX.XX  meters, 100mi is 160,934m
    altitude = models.DecimalField(max_digits=5, decimal_places=1)                       #   X,XXX.X   meters, Mt. Everest is 8,850m high
    speed = models.DecimalField(max_digits=5, decimal_places=3)                          #      XX.XXX meters/second, Usain Bolt's top speed is 12.27m/s
    heart_rate = models.IntegerField()                                                   # BPM
    cadence = models.IntegerField()                                                      # RPM
    fractional_cadence = models.DecimalField(max_digits=5, decimal_places=1)             # RPM
    enhanced_altitude = models.DecimalField(max_digits=5, decimal_places=1)              #   X,XXX.X   meters
    enhanced_speed = models.DecimalField(max_digits=5, decimal_places=3)                 #      XX.XXX meters/second


