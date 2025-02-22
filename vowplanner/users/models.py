from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User


class User(AbstractUser):
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

    REQUIRED_FIELDS = ['email', 'contact_no']

    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'vendor'})  # ✅ Ensuring only vendors are linked
    business_name = models.CharField(max_length=255)
    business_category = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=20)

    def __str__(self):
        return self.business_name

class VendorPackage(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    pkg_name = models.CharField(max_length=200)
    pkg_description = models.TextField()
    images = models.ImageField(upload_to='package_images/', null=True, blank=True)
    pkg_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.pkg_name

