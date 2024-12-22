from django.db import models
from django.contrib.auth.models import User
from calendars.models.calendar_model import Calendar

class Invitee(models.Model):
    """
    A user invited to a Calendar.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('conflict', 'Conflict'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    responded = models.BooleanField(default=False)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='pending')

    def get_choices(self):
        return self.STATUS_CHOICES