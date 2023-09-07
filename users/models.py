import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("examiner", "Examiner"),
        ("noob", "Noob"),
    )

    LEVEL_CHOICES = (
        ("junior", "Junior"),
        ("middle", "Middle"),
        ("senior", "Senior"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    )

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(_("role"), max_length=10, choices=ROLE_CHOICES, default="noob")
    status = models.CharField(_("status"), max_length=10, choices=STATUS_CHOICES, default="pending")
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
    return f"avatars/{slug}"


class Profile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    avatar = models.ImageField(upload_to=get_image_filename, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(_("birth date"), null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=10, choices=GENDER_CHOICES, default='other')

    def __str__(self):
        return self.user.email

    @property
    def filename(self):
        return os.path.basename(self.image.name)
