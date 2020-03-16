from django.db import models


class ActivityFile(models.Model):
    filename = models.CharField(max_length=15, unique=True)
    activity_type = models.CharField(max_length=20)
    activity_category = models.CharField(max_length=20)
    start_time_utc = models.DateTimeField()
    primary_file = models.BooleanField(default=True)
    secondary_activity = models.ForeignKey('self', null=True, on_delete=models.CASCADE)


class Session(models.Model):
    file = models.ForeignKey(ActivityFile, related_name='session', on_delete=models.CASCADE)
    start_time_utc = models.DateTimeField()
    start_position_lat_sem = models.IntegerField(null=True)
    start_position_long_sem = models.IntegerField(null=True)
    start_position_lat_deg = models.DecimalField(null=True, max_digits=8, decimal_places=6)
    start_position_long_deg = models.DecimalField(null=True, max_digits=9, decimal_places=6)
    start_location = models.CharField(null=True, max_length=200)
    total_elapsed_time = models.DecimalField(null=True, max_digits=10, decimal_places=3)
    total_timer_time = models.DecimalField(null=True, max_digits=10, decimal_places=3)
    total_distance = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    total_strides = models.IntegerField(null=True)
    total_cycles = models.IntegerField(null=True)
    total_calories = models.IntegerField(null=True)
    enhanced_avg_speed = models.DecimalField(null=True, max_digits=5, decimal_places=3)
    avg_speed = models.IntegerField(null=True)
    enhanced_max_speed = models.DecimalField(null=True, max_digits=5, decimal_places=3)
    max_speed = models.IntegerField(null=True)
    avg_power = models.IntegerField(null=True)
    max_power = models.IntegerField(null=True)
    total_ascent = models.IntegerField(null=True)
    total_descent = models.IntegerField(null=True)
    avg_heart_rate = models.IntegerField(null=True)
    max_heart_rate = models.IntegerField(null=True)


class ActivityData(models.Model):
    activity_walk_data_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(ActivityFile, related_name='activitydata', on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()                                               # seconds
    heart_rate = models.IntegerField()                                                   # BPM
    position_lat_sem = models.IntegerField(null=True)                                    # semicircles
    position_long_sem = models.IntegerField(null=True)                                   # semicircles
    position_lat_deg = models.DecimalField(null=True, max_digits=8, decimal_places=6)    #      XX.XXXXXX degrees
    position_long_deg = models.DecimalField(null=True, max_digits=9, decimal_places=6)   #     XXX.XXXXXX degrees
    distance = models.DecimalField(null=True, max_digits=8, decimal_places=2)            # XXX,XXX.XX  meters, 100mi is 160,934m
    altitude = models.DecimalField(null=True, max_digits=5, decimal_places=1)            #   X,XXX.X   meters, Mt. Everest is 8,850m high
    speed = models.IntegerField(null=True)                                               #      XX.XXX meters/second, Usain Bolt's top speed is 12.27m/s
    cadence = models.IntegerField(null=True)                                             # RPM
    fractional_cadence = models.DecimalField(null=True, max_digits=5, decimal_places=1)  # RPM
    enhanced_altitude = models.DecimalField(null=True, max_digits=5, decimal_places=1)   #   X,XXX.X   meters
    enhanced_speed = models.DecimalField(null=True, max_digits=5, decimal_places=3)      #      XX.XXX meters/second
