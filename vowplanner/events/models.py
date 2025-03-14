from django.db import models
from django.conf import settings
from users.models import Vendor
from packages.models import VendorPackage

class VendorEvent(models.Model):
    STATE_CHOICES = [
        ('booked', 'Booked'),
        ('on_hold', 'On Hold'),
    ]

    vendor = models.ForeignKey("users.Vendor", on_delete=models.CASCADE)
    vendor_package = models.ForeignKey("packages.VendorPackage", on_delete=models.CASCADE, null=True, blank=False)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    contact_no = models.CharField(max_length=15, null=True)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_state = models.CharField(max_length=10, choices=STATE_CHOICES, default='on_hold')
    google_event_id = models.CharField(max_length=255, blank=True, null=True)

    def update_status_from_quotation(self):
        """Automatically updates event state when a quotation is marked as paid."""
        from quotations.models import Quotation  # ✅ Import inside the method

        quotation = Quotation.objects.filter(event=self).first()
        if quotation and quotation.status == "paid":
            self.event_state = "booked"
            self.save()

    def __str__(self):
        return f"{self.event_name} - {self.get_event_state_display()}"
