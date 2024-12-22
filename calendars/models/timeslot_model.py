from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from calendars.models.calendar_model import Calendar

class Timeslot(models.Model):
    """
    A timeslot indicating user's availability for a particular Calendar.
    """
    PRIORITIES = [
        (2, "High"),
        (1, "Medium"),
        (0, "Low"),
    ]
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.IntegerField(choices=PRIORITIES)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if self.start_time.minute not in [0, 30] and self.start_time.second != 0:
            raise ValidationError({"start_time": "Timeslots must begin at the half-hour or hour mark and have 0 seconds."})
        if self.end_time.minute not in [0, 30] and self.end_time.second != 0:
            raise ValidationError({"end_time": "Timeslots must begin at the half-hour or hour mark and have 0 seconds."})
        super().save(*args, **kwargs)