import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    # Custom choices for gender, role, and level
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    ROLE_CHOICES = (
        ("examiner", "Examiner"),
        ("noob", "Noob"),
    )

    LEVEL_CHOICES = (
        ("junior", "Junior"),
        ("middle", "Middle"),
        ("senior", "Senior"),
    )

    # username = None
    email = models.EmailField(_("email address"), unique=True)
    gender = models.CharField(_("gender"), max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(_("age"), default=0)
    role = models.CharField(_("role"), max_length=10, choices=ROLE_CHOICES)
    level = models.CharField(_("level"), max_length=10, choices=LEVEL_CHOICES)
    total_tests_taken = models.PositiveIntegerField(_("total tests taken"), default=0)
    total_time_spent = models.DurationField(_("total time spent"), default=timedelta(seconds=0))
    overall_percentage = models.DecimalField(_("overall percentage"), max_digits=5, decimal_places=2, default=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


def get_image_filename(instance, filename):
    slug = slugify(filename)
    return f"products/{slug}"


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=get_image_filename, blank=True)
    bio = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.email

    @property
    def filename(self):
        return os.path.basename(self.image.name)
