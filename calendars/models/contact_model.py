from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts_user2")

