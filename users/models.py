from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('master', 'Master'),
        ('noob', 'Noob'),
    )

    LEVEL_CHOICES = (
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    total_time_spent = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.role} - ( {self.email} ) {self.first_name} {self.last_name} "
