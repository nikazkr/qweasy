# from django.db import models
# from django.contrib.auth.models import User, AbstractUser
#
# GENDER_CHOICES = [
#     ('M', 'Male'),
#     ('F', 'Female'),
#     ('O', 'Other'),
# ]
#
#
# class CustomUser(AbstractUser):
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
#     age = models.PositiveIntegerField()
#
#     def __str__(self):
#         return self.user.email  # Display user's email in admin panel
