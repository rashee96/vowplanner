from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    )

    customer_name = models.CharField(max_length=255, blank=True, null=True)
    vendor_name = models.CharField(max_length=255, blank=True, null=True)  # New Column
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
    is_approved = models.BooleanField(default=False)  # For admin approval
    google_authorized = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'contact_no']

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'vendor'}
    )  
    business_name = models.CharField(max_length=255)
    business_category = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=20)

    def __str__(self):
        return self.business_name


class UnavailableDate(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return str(self.date)
