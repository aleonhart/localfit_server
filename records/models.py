from django.db import models


class RecordsFile(models.Model):
    sport = models.CharField(max_length=20, unique=True)
    calories = models.IntegerField(null=True)
    distance = models.IntegerField(null=True)
    timer_time = models.IntegerField(null=True)


