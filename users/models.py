from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
        Custom user model representing users of the application.
    """

    class Role(models.TextChoices):
        EXAMINER = 'examiner', 'Examiner'
        NOOB = 'noob', 'Noob'

    class Level(models.TextChoices):
        JUNIOR = 'junior', 'Junior'
        MIDDLE = 'middle', 'Middle'
        SENIOR = 'senior', 'Senior'

    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    @staticmethod
    def default_duration():
        return timedelta(seconds=0)

    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    level = models.CharField(max_length=10, choices=Level.choices, null=True, blank=True)
    total_tests_taken = models.PositiveIntegerField(default=0)
    total_time_spent = models.DurationField(default=default_duration())
    overall_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)

    def __str__(self):
        return f"{self.role} - ( {self.email} ) {self.first_name} {self.last_name} - {self.username}"
