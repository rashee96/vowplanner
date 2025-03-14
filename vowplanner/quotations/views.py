from datetime import datetime, timedelta
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import QuotationForm, QuotationLineForm
from django.forms import inlineformset_factory
from .models import Quotation, QuotationLine
from events.models import VendorEvent

@login_required
def create_quotation(request, event_id):
    event = get_object_or_404(VendorEvent, id=event_id, vendor=request.user.vendor)

    if request.method == "POST":
        form = QuotationForm(request.POST)
        QuotationLineFormSet = inlineformset_factory(Quotation, QuotationLine,
                                                     form=QuotationLineForm, extra=1)
        formset = QuotationLineFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            quotation = form.save(commit=False)
            quotation.vendor = event.vendor
            quotation.event = event
            quotation.customer_user = event.customer_user
            quotation.customer_name = event.customer_name
            quotation.vendor_package = event.vendor_package
            quotation.event_name = event.event_name
            quotation.event_date = event.event_date
            quotation.save()

            formset.instance = quotation
            formset.save()

            return redirect('quotations:view_quotation', quotation.id)

    else:
        form = QuotationForm()
        QuotationLineFormSet = inlineformset_factory(Quotation, QuotationLine,
                                                     form=QuotationLineForm, extra=1)
        formset = QuotationLineFormSet()

    return render(request, 'quotations/create_quotation.html',
                  {'form': form, 'formset': formset, 'event': event})

@login_required
def view_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    if quotation.confirmed_date:
        is_valid = bool(quotation.confirmed_date + timedelta(days=7) > datetime.now().date())
    else:
        is_valid = False
    user_type = request.user.user_type
    return render(request, 'quotations/view_quotation.html', {'quotation': quotation, 'is_valid': is_valid, 'user_type': user_type})

@login_required
def confirm_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, vendor=request.user.vendor)

    if quotation.status == "draft":
        quotation.status = "confirmed"
        quotation.confirmed_date = timezone.now()
        quotation.save()

    return redirect('quotations:view_quotation', quotation_id=quotation.id)

@login_required
def accept_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, customer_user=request.user)

    if quotation.status == "confirmed" and quotation.event_date >= timezone.now().date():
        quotation.status = "accepted"
        quotation.save()

    return redirect('quotations:view_quotation', quotation_id=quotation.id)


@login_required
def submit_payment(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, customer_user=request.user)

    if request.method == "POST":
        quotation.customer_note = request.POST.get("customer_note", "")
        quotation.receipt_attachment = request.FILES.get("receipt_attachment")
        quotation.status = "in_payment"
        quotation.save()

    return redirect('quotations:view_quotation', quotation_id=quotation.id)


@login_required
def mark_as_paid(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, vendor=request.user.vendor)

    if quotation.status == "in_payment":
        quotation.status = "paid"
        quotation.event.event_state = "booked"  # Mark event as booked
        quotation.event.save()
        quotation.save()

    return redirect('quotations:view_quotation', quotation_id=quotation.id)
