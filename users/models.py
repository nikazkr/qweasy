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

    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    level = models.CharField(max_length=10, choices=Level.choices, null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    total_time_spent = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.role} - ( {self.email} ) {self.first_name} {self.last_name} - {self.username}"
