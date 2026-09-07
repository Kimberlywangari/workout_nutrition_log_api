from django.contrib import admin

# Register your models here.
from .models import BodyMeasurement, Profile, WorkOut

admin.site.register(WorkOut)
admin.site.register(BodyMeasurement)
admin.site.register(Profile)

