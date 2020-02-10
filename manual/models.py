from django.db import models


class ManualStats(models.Model):
    """
    Data that is not supplied by Garmin
    but can easily be entered manually
    """
    vo2_max = models.DecimalField(null=True, max_digits=3, decimal_places=1)
    weight_lbs = models.DecimalField(null=True, max_digits=4, decimal_places=1)
    height_inches = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
