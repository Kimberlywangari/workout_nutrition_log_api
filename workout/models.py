from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class WorkOut(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=55)
    calories_burnt = models.FloatField(null=True, blank=True)
    duration = models.FloatField()
    date = models.DateField()
    location = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.user.username} - {self.workout_type} - {self.date}"

    class Meta:
        ordering = ['-date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(duration__gt=0),
                name='workout_duration_positive',
            ),
            models.CheckConstraint(
                check=models.Q(calories_burnt__gte=0),
                name='workout_calories_nonnegative',
            ),
        ]


class BodyMeasurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    body_fat_percentage = models.FloatField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.weight} - {self.date}"

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'], name='unique_bodymeasurement_per_user_per_day'
            ),
            models.CheckConstraint(
                check=models.Q(weight__gt=0), name='bodymeasurement_weight_positive'
            ),
            models.CheckConstraint(
                check=models.Q(height__gt=0), name='bodymeasurement_height_positive'
            ),
            models.CheckConstraint(
                check=models.Q(body_fat_percentage__gte=0) & models.Q(body_fat_percentage__lte=100),
                name='bodymeasurement_bodyfat_in_range',
            ),
        ]


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ... WorkOut and BodyMeasurement unchanged ...

class Profile(models.Model):
    ROLE_CHOICES = [('trainer', 'Trainer'), ('trainee', 'Trainee')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='trainee')
    trainer = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='trainees'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(age__gte=0), name='profile_age_nonnegative'),
        ]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)