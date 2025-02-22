from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomerRegistrationForm, VendorRegistrationForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VendorPackage
from .forms import VendorPackageForm
from django.contrib import messages


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
            return redirect('home')
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
            user = User.objects.get(username=username)
            user.password = make_password(new_password)  # Hash the password
            user.save()
            messages.success(request, "Password reset successfully! Please log in with your new password.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot_password')

    return render(request, 'users/forgot_password.html')



@login_required
def vendor_dashboard(request):
    """Vendor Dashboard - Shows existing packages and allows CRUD operations"""
    if request.user.user_type != 'vendor':  # ✅ Check user_type instead of hasattr
        return redirect('home')  # Redirect non-vendors to home

    packages = VendorPackage.objects.filter(vendor__user=request.user)
    return render(request, 'users/vendor_dashboard.html', {'packages': packages})


@login_required
def create_vendor_package(request):
    """Create a new Vendor Package"""
    if request.user.user_type != 'vendor':  # ✅ Ensure only vendors can create packages
        return redirect('home')

    if request.method == 'POST':
        form = VendorPackageForm(request.POST, request.FILES)

        if form.is_valid():
            package = form.save(commit=False)
            package.user = request.user  # ✅ Link package to vendor user directly
            package.save()
            messages.success(request, "Vendor Package Created Successfully!")
            return redirect('vendor_dashboard')
    else:
        form = VendorPackageForm()
    
    return render(request, 'users/vendor_package_form.html', {'form': form, 'title': 'Create Package'})

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

@login_required
def archive_vendor_package(request, package_id):
    """Archive a Vendor Package"""
    package = get_object_or_404(VendorPackage, id=package_id, vendor=request.user.vendor)
    package.is_archived = True
    package.save()
    messages.success(request, "Vendor Package Archived Successfully!")
    return redirect('vendor_dashboard')


