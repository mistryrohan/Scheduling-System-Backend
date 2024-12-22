from django.db import models
from django.contrib.auth.models import User
from calendars.models.calendar_model import Calendar

class Meeting(models.Model):
    """
    The final Meeting for user, with calendar's primary_user.
    Inherits calendar's name & description.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    duration = models.IntegerField() # In minutes
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)