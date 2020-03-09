# coding=utf-8
from django.db import models


class MonitorFile(models.Model):
    """
    MONITOR files
    """
    filename = models.CharField(max_length=15, unique=True)


class StressData(models.Model):
    """
    Stress data from MONITOR files
    """
    monitor_stress_data_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(MonitorFile, on_delete=models.CASCADE)
    stress_level_time_utc = models.DateTimeField()
    stress_level_value = models.IntegerField()


class HeartRateData(models.Model):
    """
    Heart rate data from MONITOR files
    """

    heart_rate_data_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(MonitorFile, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    heart_rate = models.IntegerField()


class RestingMetRateData(models.Model):
    """
    Resting metabolic rate data from MONITOR files
    """

    resting_metabolic_rate_data_id = models.AutoField(primary_key=True)
    file = models.ForeignKey(MonitorFile, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    resting_metabolic_rate = models.IntegerField()  # KCAL


class StepData(models.Model):
    """
    Daily step data from MONITOR files
    """

    step_data_id = models.AutoField(primary_key=True)
    date = models.DateField()
    steps = models.IntegerField(null=True)
