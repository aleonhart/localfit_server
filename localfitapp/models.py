# coding=utf-8
from django.db import models


class MonitorStressFile(models.Model):
    """
    Heart rate monitor files (MONITOR) - Stress Data
    """
    filename = models.CharField(max_length=15, unique=True)


class MonitorStressData(models.Model):
    """
    Stress data from heart rate monitor files (MONITOR)

    Field 0="Data"
    Field 2="stress_level"
    Field 3="stress_level_time"
    Field 4=timestamp
    Field 5=units "s"
    Field 6="stress_level_value"
    Field 7=value (0-100)
    Field 8=units
    Field 9="unknown"
    Field 10=-100 to 150

    Date is Tuesday, October 26, 1999. 20 years behind.
    """
    gvamonitordata_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(MonitorStressFile, on_delete=models.CASCADE)
    stress_level_time = models.DateTimeField()  # Field 4
    stress_level_value = models.IntegerField()  # Field 7
