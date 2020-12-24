from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your models here.
class Activity(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=True)
    start_date = models.DateField()
    start_date_local = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    distance = models.FloatField()
    moving_time = models.PositiveIntegerField(null=True)
    elapsed_time = models.PositiveIntegerField(null=True)
    total_elevation_gain = models.FloatField(null=True)
    activity_type = models.CharField(max_length=30, null=True)
    average_speed = models.FloatField(null=True)
    max_speed = models.FloatField(null=True)
    elev_high = models.FloatField(null=True)
    elev_low = models.FloatField(null=True)

    class Meta:
        db_table = 'activity'


class RewardHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    reward_amount = models.IntegerField()

    class Meta:
        db_table = 'reward_history'


class GithonFee(models.Model):
    reward_per_km = models.PositiveIntegerField()
    lose_per_km = models.PositiveIntegerField()

    class Meta:
        db_table = 'githon_fee'
