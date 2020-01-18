from django.db import models


class ActivityWalkFile(models.Model):
    """
    Activity Walk files (ACTIVITY)
    """
    filename = models.CharField(max_length=15, unique=True)
    activity_type = models.CharField(default="walk", max_length=20)
    display_name = models.CharField(max_length=15, unique=True)


class ActivityWalkSession(models.Model):
    file = models.ForeignKey(ActivityWalkFile, related_name='activitywalksession', on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    start_time_utc = models.DateTimeField()
    start_position_lat_sem = models.IntegerField(null=True)
    start_position_long_sem = models.IntegerField(null=True)
    start_position_lat_deg = models.DecimalField(null=True, max_digits=17, decimal_places=14)
    start_position_long_deg = models.DecimalField(null=True, max_digits=17, decimal_places=14)
    total_elapsed_time = models.DecimalField(null=True, max_digits=7, decimal_places=3)
    total_timer_time = models.DecimalField(null=True, max_digits=7, decimal_places=3)
    total_distance = models.DecimalField(max_digits=8, decimal_places=2)
    total_strides = models.IntegerField(null=True)
    total_calories = models.IntegerField(null=True)
    enhanced_avg_speed = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    avg_speed = models.IntegerField(null=True)
    enhanced_max_speed = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    max_speed = models.IntegerField(null=True)
    avg_power = models.IntegerField(null=True)
    max_power = models.IntegerField(null=True)
    total_ascent = models.IntegerField(null=True)
    total_descent = models.IntegerField(null=True)


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
    file = models.ForeignKey(ActivityWalkFile, related_name='activitywalkdata', on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()                                               # seconds
    position_lat_sem = models.IntegerField(null=True)                                    # semicircles
    position_long_sem = models.IntegerField(null=True)                                   # semicircles
    position_lat_deg = models.DecimalField(null=True, max_digits=8, decimal_places=6)    #      XX.XXXXXX degrees
    position_long_deg = models.DecimalField(null=True, max_digits=9, decimal_places=6)   #     XXX.XXXXXX degrees
    distance = models.DecimalField(max_digits=8, decimal_places=2)                       # XXX,XXX.XX  meters, 100mi is 160,934m
    altitude = models.DecimalField(max_digits=5, decimal_places=1)                       #   X,XXX.X   meters, Mt. Everest is 8,850m high
    speed = models.IntegerField()                                                        #      XX.XXX meters/second, Usain Bolt's top speed is 12.27m/s
    heart_rate = models.IntegerField()                                                   # BPM
    cadence = models.IntegerField()                                                      # RPM
    fractional_cadence = models.DecimalField(max_digits=5, decimal_places=1)             # RPM
    enhanced_altitude = models.DecimalField(max_digits=5, decimal_places=1)              #   X,XXX.X   meters
    enhanced_speed = models.DecimalField(max_digits=5, decimal_places=3)                 #      XX.XXX meters/second


