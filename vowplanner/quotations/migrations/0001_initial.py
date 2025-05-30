# Generated by Django 5.1.6 on 2025-03-14 17:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('packages', '0001_initial'),
        ('users', '0011_remove_quotationline_quotation_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=255)),
                ('event_name', models.CharField(max_length=255)),
                ('event_date', models.DateField()),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('accepted', 'Accepted'), ('in_payment', 'In Payment'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='draft', max_length=15)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('net_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_method', models.TextField()),
                ('receipt_attachment', models.FileField(blank=True, null=True, upload_to='receipts/')),
                ('customer_note', models.TextField(blank=True, null=True)),
                ('confirmed_date', models.DateField(blank=True, null=True)),
                ('customer_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='quotation', to='events.vendorevent')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.vendor')),
                ('vendor_package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='packages.vendorpackage')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='quotations.quotation')),
            ],
        ),
    ]
