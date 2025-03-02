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
import json
from django.views.decorators.csrf import csrf_exempt
from users.models import UnavailableDate
import os
import json
import datetime
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
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

@login_required
def google_auth(request):
    """Initiates Google OAuth authentication process"""
    if 'google_credentials' in request.session:
        del request.session['google_credentials']
        request.user.google_authorized = False  # Reset authorization status
        request.user.save()

    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_FILE,
        scopes=settings.GOOGLE_CALENDAR_SCOPES,
        redirect_uri="http://localhost:8000/users/oauth/callback/"
    )

    auth_url, _ = flow.authorization_url(prompt='consent')  # ✅ Force user consent
    return redirect(auth_url)

@login_required
def google_auth_callback(request):
    """Handles the Google OAuth callback and stores credentials"""
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_FILE,
        scopes=settings.GOOGLE_CALENDAR_SCOPES,
        redirect_uri="http://localhost:8000/users/oauth/callback/"
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials

    # ✅ Ensure refresh_token is saved (Google may not return it on every request)
    if not credentials.refresh_token:
        stored_credentials = request.session.get('google_credentials', {})
        credentials.refresh_token = stored_credentials.get('refresh_token')  # Use old refresh token if missing

    request.session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # ✅ Mark user as authorized
    user = request.user
    user.google_authorized = True
    user.save()

    return redirect('vendor_dashboard')

@login_required
def fetch_google_calendar_events(request):
    """Fetches only events created by Vow Planner"""
    credentials_data = request.session.get('google_credentials')

    if not credentials_data:
        return JsonResponse({'error': 'User not authenticated with Google'}, status=401)

    try:
        credentials = Credentials(**credentials_data)
        service = build("calendar", "v3", credentials=credentials)

        now = datetime.datetime.utcnow().isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        # ✅ Filter only events that contain the "Created by Vow Planner" marker
        vow_planner_events = []
        print(json.dumps(events, indent=4))  # Debugging step: Print all fetched events
        for event in events:
            description = event.get("description", "").lower()
            extended_properties = event.get("extendedProperties", {}).get("private", {})

            if (
                "created by vow planner" in description or
                extended_properties.get("created_by") == "vowplanner"
            ):
                vow_planner_events.append({
                    "id": event["id"],
                    "title": event["summary"],
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date"))
                })

        return JsonResponse(vow_planner_events, safe=False)

    except Exception as e:
        return JsonResponse({'error': f'Google API Error: {str(e)}'}, status=500)

@login_required
def add_google_calendar_event(request):
    """Adds an event to Google Calendar with a Vow Planner identifier"""
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    credentials_data = request.session.get('google_credentials')

    if not credentials_data:
        return JsonResponse({'error': 'User not authenticated with Google'}, status=401)

    credentials = Credentials(**credentials_data)
    service = build("calendar", "v3", credentials=credentials)

    data = json.loads(request.body)
    event_title = data.get("title")
    event_date = data.get("date")

    if not event_title or not event_date:
        return JsonResponse({'error': 'Missing event details'}, status=400)

    event_body = {
        "summary": event_title,
        "description": "Created by Vow Planner",  # ✅ Add this to help filtering later
        "start": {"date": event_date},
        "end": {"date": event_date},
        "extendedProperties": {
            "private": {
                "created_by": "vowplanner"  # ✅ Add structured metadata for filtering
            }
        }
    }

    created_event = service.events().insert(calendarId="primary", body=event_body).execute()

    return JsonResponse({"success": True, "event_id": created_event["id"]})

@login_required
def delete_google_calendar_event(request):
    """Deletes an event from Google Calendar"""
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    credentials_data = request.session.get('google_credentials')

    if not credentials_data:
        return JsonResponse({'error': 'User not authenticated with Google'}, status=401)

    credentials = Credentials(**credentials_data)
    service = build("calendar", "v3", credentials=credentials)

    data = json.loads(request.body)
    event_id = data.get("event_id")

    if not event_id:
        return JsonResponse({'error': 'Missing event ID'}, status=400)

    service.events().delete(calendarId="primary", eventId=event_id).execute()

    return JsonResponse({"success": True})

def clear_google_credentials(request):
    """Clears stored Google credentials from session"""
    if 'google_credentials' in request.session:
        del request.session['google_credentials']
    return redirect('google_auth')