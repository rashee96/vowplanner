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

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate input
        if not username or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('forgot_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('forgot_password')

        try:
            user = CustomUser.objects.get(username=username)
            user.password = make_password(new_password)  # Hash the password
            user.save()
            messages.success(request, "Password reset successfully! Please log in with your new password.")
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot_password')

    return render(request, 'users/forgot_password.html')

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
