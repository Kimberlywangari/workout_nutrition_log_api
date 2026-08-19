from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class WorkOut(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=55)
    calories_burnt = models.FloatField(null=True, blank=True)
    duration = models.FloatField()
    date = models.DateField()
    location = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.user.username} - {self.workout_type} - {self.date}"

class BodyMeasurement(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    body_fat_percentage = models.FloatField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.weight} - {self.date}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username} - {self.age} - {self.gender}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)