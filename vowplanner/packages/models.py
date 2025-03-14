from django.db import models
from users.models import Vendor

class VendorPackage(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    pkg_name = models.CharField(max_length=200)
    pkg_description = models.TextField()
    images = models.ImageField(upload_to='package_images/', null=True, blank=True)
    pkg_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_archived = models.BooleanField(default=False)
    #archive_reason = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.pkg_name
