from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    drivers_license = models.ImageField(upload_to='licenses/', blank=True, null=True)
    utility_bill = models.ImageField(upload_to='utility_bills/', blank=True, null=True)

class Letter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    letter_file = models.FileField(upload_to='letters/', blank=True, null=True)
    dispute_reason = models.TextField()
    letter_sent = models.BooleanField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
