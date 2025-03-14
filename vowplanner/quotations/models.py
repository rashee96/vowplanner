from django.db import models
from django.conf import settings
from users.models import Vendor
from events.models import VendorEvent

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('accepted', 'Accepted'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    vendor = models.ForeignKey('users.Vendor', on_delete=models.CASCADE)  # Use string reference
    event = models.OneToOneField('events.VendorEvent', on_delete=models.CASCADE, related_name='quotation')  # Use string reference
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    vendor_package = models.ForeignKey('packages.VendorPackage', on_delete=models.CASCADE)  # ✅ Correct reference
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.TextField()
    receipt_attachment = models.FileField(upload_to='receipts/', null=True, blank=True)  # Payment receipt upload
    customer_note = models.TextField(null=True, blank=True)  # Optional customer note
    confirmed_date = models.DateField(null=True, blank=True)  # Allow NULL values

    def __str__(self):
        return f"Quotation for {self.customer_name} - {self.event_name}"

class QuotationLine(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='lines')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.price}"
