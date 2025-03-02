from pyexpat.errors import messages

from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomerRegistrationForm, VendorRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VendorPackage, CustomUser
from .forms import VendorPackageForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from users.models import UnavailableDate



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
            return redirect('vendor_dashboard')
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
                return redirect('vendor_dashboard')  # Redirect vendors
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
    #return render(request, 'users/home.html', {'user': request.user})
    context = {} 
    
    if request.user.is_authenticated:
        context['user_name'] = request.user.customer_name or request.user.username  

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
    """Vendor Dashboard - Shows only active packages"""
    if request.user.user_type != 'vendor':  
        return redirect('home')  

    packages = VendorPackage.objects.filter(vendor__user=request.user, is_archived=False)
    return render(request, 'users/vendor_dashboard.html', {'packages': packages})


@login_required
def create_vendor_package(request):
    """Create a new Vendor Package"""
    if request.user.user_type != 'vendor':  # ✅ Ensure only vendors can create packages
        return redirect('home')

    vendor = getattr(request.user, 'vendor', None)  # ✅ Fetch the vendor profile
    if not vendor:
        messages.error(request, "Vendor profile not found.")
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = VendorPackageForm(request.POST, request.FILES)

        if form.is_valid():
            package = form.save(commit=False)
            package.vendor = vendor  # ✅ Assign the Vendor object, NOT the user
            package.save()
            messages.success(request, "Vendor Package Created Successfully!")
            return redirect('vendor_dashboard')
    else:
        form = VendorPackageForm()

    return render(request, 'users/vendor_package_form.html',
                  {'form': form, 'title': 'Create Package'})

@login_required
def update_vendor_package(request, package_id):
    """Update an existing Vendor Package"""
    package = get_object_or_404(VendorPackage, id=package_id, vendor=request.user.vendor)
    
    if request.method == 'POST':
        form = VendorPackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor Package Updated Successfully!")
            return redirect('vendor_dashboard')
    else:
        form = VendorPackageForm(instance=package)
    
    return render(request, 'users/vendor_package_form.html', {'form': form, 'title': 'Update Package'})
def category_packages(request, category):
    category_images = {
        "venues": "wedding_venue.jpg",
        "photography": "wedding_photography.jpg",
        "videography": "wedding_videography.jpg",
        "wedding_favors": "wedding_favours.jpg",
        "wedding_cake": "wedding_cake.jpg",
        "entertainment": "entertainment.jpg"
    }
    category_banner_name = {
        "venues": "Venue",
        "photography": "Photography",
        "videography": "Videography",
        "wedding_favors": "Wedding Favor",
        "wedding_cake": "Wedding Cake",
        "entertainment": "Entertainment"
    }
    banner_image = category_images.get(category, "default_banner.jpg")
    category_banner_name = category_banner_name.get(category, "Category")

    packages = VendorPackage.objects.filter(vendor__business_category=category, is_archived=False)

    return render(request, 'users/category_packages.html', {
        'category': category,
        'packages': packages,
        'banner_image': banner_image,
        'category_name': category_banner_name
    })

    
def package_detail(request, package_id):
    """View for displaying details of a specific package"""
    package = get_object_or_404(VendorPackage, id=package_id)
    return render(request, 'users/package_detail.html', {'package': package})


@login_required
def archive_vendor_package(request, package_id):
    """Archive a Vendor Package"""
    if request.method == "POST":
        package = get_object_or_404(VendorPackage, id=package_id, vendor=request.user.vendor)
        data = json.loads(request.body)
        reason = data.get("reason", "")

        if not reason:
            return JsonResponse({"success": False, "error": "Reason is required"}, status=400)

        package.is_archived = True
        package.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

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