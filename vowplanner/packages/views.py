import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import VendorPackage
from .forms import VendorPackageForm
from events.models import VendorEvent
from users.models import Vendor

@login_required
def all_vendor_packages(request):
    """Show all vendor packages with search, type, price, and event date filters."""
    packages = VendorPackage.objects.filter(is_archived=False)

    # Get search parameters
    search_query = request.GET.get('search', '').strip()
    package_type = request.GET.get('package_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    selected_date = request.GET.get('event_date', '')

    # Filter by search query (Name or Package Name)
    if search_query:
        packages = packages.filter(pkg_name__icontains=search_query)

    # Filter by package type
    vendor_types = Vendor.objects.values_list('business_category', flat=True).distinct()
    if package_type:
        packages = packages.filter(vendor__business_category=package_type)

    # Apply Min Price filter
    if min_price.isdigit():
        packages = packages.filter(pkg_price__gte=int(min_price))

    # Apply Max Price filter
    if max_price.isdigit():
        packages = packages.filter(pkg_price__lte=int(max_price))

    # Exclude packages that already have an event on the selected date
    if selected_date:
        booked_packages = VendorEvent.objects.filter(event_date=selected_date).values_list('vendor_package', flat=True)
        packages = packages.exclude(id__in=booked_packages)

    context = {
        'packages': packages,
        'search_query': search_query,
        'vendor_types': vendor_types,
        'selected_type': package_type,
        'min_price': min_price,
        'max_price': max_price,
        'selected_date': selected_date,
    }

    return render(request, 'packages/all_vendor_packages.html', context)



@login_required
def get_vendor_availability(request, package_id):
    """Fetch unavailable dates for a specific package"""
    booked_dates = VendorEvent.objects.filter(vendor_package_id=package_id).values_list('event_date', flat=True)

    events = [{"title": "Unavailable", "start": str(date), "backgroundColor": "#ff0000"} for date in booked_dates]

    return JsonResponse(events, safe=False)

@login_required
def create_vendor_package(request):
    """Create a new Vendor Package"""
    if request.user.user_type != 'vendor':  # ✅ Ensure only vendors can create packages
        return redirect('home')

    vendor = getattr(request.user, 'vendor', None)  # ✅ Fetch the vendor profile
    if not vendor:
        messages.error(request, "Vendor profile not found.")
        return redirect('users:vendor_dashboard')

    if request.method == 'POST':
        form = VendorPackageForm(request.POST, request.FILES)

        if form.is_valid():
            package = form.save(commit=False)
            package.vendor = vendor  # ✅ Assign the Vendor object, NOT the user
            package.save()
            messages.success(request, "Vendor Package Created Successfully!")
            return redirect('users:vendor_dashboard')
    else:
        form = VendorPackageForm()

    return render(request, 'packages/vendor_package_form.html',
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
            return redirect('users:vendor_dashboard')
    else:
        form = VendorPackageForm(instance=package)

    return render(request, 'packages/vendor_package_form.html',
                  {'form': form, 'title': 'Update Package'})


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

    return render(request, 'packages/category_packages.html', {
        'category': category,
        'packages': packages,
        'banner_image': banner_image,
        'category_name': category_banner_name
    })


def package_detail(request, package_id):
    """View for displaying details of a specific package"""
    package = get_object_or_404(VendorPackage, id=package_id)
    return render(request, 'packages/package_detail.html', {'package': package})


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

