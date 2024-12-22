from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

class Calendar(models.Model):
    """
    Primary_user's tentative Meeting.
    """
    primary_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="primary_user_calendar")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256, default='')
    duration = models.IntegerField(default=30)
    
    def save(self, *args, **kwargs):
        if self.duration % 30 != 0:
            raise ValidationError("Meeting duration must be a multiple of 30.")
        super().save(*args, **kwargs)