from pyexpat.errors import messages

from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout
from .forms import CustomerRegistrationForm, VendorRegistrationForm, LoginForm
from .models import CustomUser
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from users.models import UnavailableDate
import os
import json
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from events.models import VendorEvent
from packages.models import VendorPackage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'users/customer_register.html', {'form': form})

def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if hasattr(user, 'vendor'):
                vendor = user.vendor
                vendor.business_category = vendor.business_category.lower()
                vendor.save()

            login(request, user)
            return redirect('users:vendor_dashboard')
    else:
        form = VendorRegistrationForm()

    return render(request, 'users/vendor_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ✅ Check user type instead of hasattr(user, 'vendor')
            if user.user_type == 'vendor':
                return redirect('users:vendor_dashboard')  # Redirect vendors
            else:
                return redirect('home')  # Redirect customers

    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render

def home(request):
    """Render the home page with user details if authenticated."""
    context = {}

    if request.user.is_authenticated:
        context['user_name'] = request.user.customer_name or request.user.username
        context['user_type'] = request.user.user_type

    return render(request, 'users/home.html', context)

@login_required
def vendor_dashboard(request):
    """Vendor Dashboard with package details & event records."""
    if request.user.user_type != 'vendor':
        return redirect('home')

    packages = VendorPackage.objects.filter(vendor__user=request.user, is_archived=False)
    events = VendorEvent.objects.filter(vendor=request.user.vendor)

    return render(request, 'users/vendor_dashboard.html', {
        'packages': packages,
        'events': events
    })

@csrf_exempt
def save_unavailable_dates(request):
    if request.method == "POST":
        data = json.loads(request.body)
        unavailable_dates = data.get("unavailable_dates", [])

        # Save unavailable dates in the database
        UnavailableDate.objects.all().delete()  # Remove previous entries
        for date in unavailable_dates:
            UnavailableDate.objects.create(date=date)

        return JsonResponse({"message": "Unavailable dates saved successfully."})

    return JsonResponse({"error": "Invalid request"}, status=400)

# Send reset link
def forgot_password_request(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        try:
            user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=identifier)
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('users:forgot_password_request')

        # Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset URL
        domain = get_current_site(request).domain
        reset_link = f"http://{domain}{reverse('users:reset_password', kwargs={'uidb64': uid})}"

        subject = "Reset Your Password"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        # Now render the email HTML
        html_content = render_to_string('users/password_reset_email.html', {
            'user': user,
            'reset_link': reset_link,
        })

        # Use EmailMultiAlternatives
        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, "Reset link sent to your email.")
        return redirect('users:login')

    return render(request, 'users/password_reset_request.html')

# Reset password form
def reset_password(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('users:reset_password', uidb64=uidb64)

        if user:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully! Please log in.")
            return redirect('users:login')
        else:
            messages.error(request, "Invalid reset link.")
            return redirect('users:login')

    return render(request, 'users/reset_password.html')
