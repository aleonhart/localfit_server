# coding=utf-8
from django.db import models


# Garmin vívoactive 3 Models
class GVAMonitorFile(models.Model):
    """
    Heart rate monitor files (MONITOR)
    """
    filename = models.CharField(max_length=15)


class GVAMonitorData(models.Model):
    """
    Data fron heart rate monitor files (MONITOR)
    """
    gvamonitordata_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(GVAMonitorFile, on_delete=models.CASCADE)
    type = models.CharField(max_length=15)
    local_number = models.IntegerField()
    message = models.CharField(max_length=30)
    field_1 = models.CharField(max_length=30)
    value_1 = models.IntegerField()
    units_1 = models.CharField(max_length=2)
    field_2 = models.CharField(max_length=30)
    value_2 = models.IntegerField()
    units_2 = models.CharField(max_length=2)
    field_3 = models.CharField(max_length=30)
    value_3 = models.IntegerField()
    units_3 = models.CharField(max_length=2)
    field_4 = models.CharField(max_length=30)  # here and below seemingly unused
    value_4 = models.IntegerField()
    units_4 = models.CharField(max_length=2)
    field_5 = models.CharField(max_length=30)
    value_5 = models.IntegerField()
    units_5 = models.CharField(max_length=2)
    field_6 = models.CharField(max_length=30)
    value_6 = models.IntegerField()
    units_6 = models.CharField(max_length=2)
    field_7 = models.CharField(max_length=30)
    value_7 = models.IntegerField()
    units_7 = models.CharField(max_length=2)
    field_8 = models.CharField(max_length=30)
    value_8 = models.IntegerField()
    units_8 = models.CharField(max_length=2)

