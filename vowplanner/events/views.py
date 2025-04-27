import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.conf import settings
from .models import VendorEvent
from quotations.models import Quotation, QuotationLine
from packages.models import VendorPackage
from users.models import CustomUser
from quotations.forms import QuotationForm, QuotationLineForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@login_required
def get_all_events(request):
    """Fetch all DB-stored events for FullCalendar."""
    events = VendorEvent.objects.filter(vendor=request.user.vendor)

    event_list = []
    for event in events:
        event_list.append({
            "id": event.id,
            "title": event.event_name,
            "start": event.event_date.isoformat(),
            "backgroundColor": "#28a745" if event.event_state == "booked" else "#ffc107",
            "borderColor": "#28a745" if event.event_state == "booked" else "#ffc107",
            "state": event.event_state  # Explicitly send state
        })

    return JsonResponse(event_list, safe=False)

@login_required
def create_event(request):
    """Adds an event to Google Calendar and saves it in the Django database."""
    data = json.loads(request.body)
    event_title = data.get("title")
    event_date = data.get("date")
    customer_name = data.get("customer_name", "Unknown")
    contact_no = data.get("contact_no", "Unknown")
    customer_email = data.get("email", "")
    vendor_package_id = data.get("vendor_package", None)  # Get vendor package
    state = data.get("status", "on_hold")

    try:
        vendor_package = VendorPackage.objects.get(id=vendor_package_id, vendor=request.user.vendor)
    except VendorPackage.DoesNotExist:
        return JsonResponse({'error': 'Invalid vendor package selected'}, status=400)

    google_event_id = False
    customer_user = CustomUser.objects.filter(email=customer_email).first()

    # Save event to the database
    new_event = VendorEvent.objects.create(
        vendor=request.user.vendor,
        vendor_package=vendor_package,  # Store the selected vendor package
        customer_name=customer_name,
        email=customer_email,
        customer_user=customer_user,
        contact_no=contact_no,
        event_name=event_title,
        event_date=event_date,
        event_state=state,
        google_event_id=google_event_id
    )

    send_event_emails(
        vendor=request.user.vendor,
        customer_email=customer_email,
        customer_name=customer_name,
        event_name=event_title,
        event_date=event_date,
        package_name=vendor_package.pkg_name
    )

    return JsonResponse({"success": True, "event_id": google_event_id, "db_event_id": new_event.id})

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

@login_required
def user_booking_list(request):
    """Displays all bookings made by the logged-in user"""
    bookings = VendorEvent.objects.filter(customer_user=request.user).order_by("-event_date")

    return render(request, 'events/user_booking_list.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    """Handles booking deletion"""
    booking = get_object_or_404(VendorEvent, id=booking_id, customer_user=request.user)

    # Delete from Google Calendar if it exists
    if booking.google_event_id:
        credentials_data = request.session.get("google_credentials")
        if credentials_data:
            credentials = Credentials(**credentials_data)
            service = build("calendar", "v3", credentials=credentials)

            try:
                service.events().delete(calendarId="primary", eventId=booking.google_event_id).execute()
            except Exception as e:
                return JsonResponse({"error": f"Failed to delete Google Calendar event: {str(e)}"}, status=500)

    booking.delete()
    return JsonResponse({"success": True})



@login_required
def fetch_and_save_google_events(request):
    """Fetch events from Google Calendar & save them in the DB."""
    credentials_data = request.session.get('google_credentials')
    if not credentials_data:
        return JsonResponse({'error': 'User not authenticated with Google'}, status=401)

    credentials = Credentials(**credentials_data)
    service = build("calendar", "v3", credentials=credentials)

    now = datetime.utcnow().isoformat() + "Z"

    try:
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        saved_events = []

        for event in events:
            google_event_id = event.get("id")
            summary = event.get("summary", "Unnamed Event")
            start_date = event.get("start", {}).get("date", None)

            if start_date:
                # Check if event already exists
                existing_event = VendorEvent.objects.filter(google_event_id=google_event_id).first()
                if not existing_event:
                    # Save in DB
                    new_event = VendorEvent.objects.create(
                        vendor=request.user.vendor,
                        customer_name="Unknown",  # Update manually later
                        contact_no="Unknown",
                        event_name=summary,
                        event_date=start_date,
                        event_state="on_hold",
                        google_event_id=google_event_id
                    )
                    saved_events.append(new_event.id)

        return JsonResponse({'success': True, 'saved_events': saved_events})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        redirect_uri="http://localhost:8000/events/oauth/callback/"
    )

    auth_url, _ = flow.authorization_url(prompt='consent')  # ✅ Force user consent
    return redirect(auth_url)

@login_required
def google_auth_callback(request):
    """Handles the Google OAuth callback and stores credentials"""
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_FILE,
        scopes=settings.GOOGLE_CALENDAR_SCOPES,
        redirect_uri="http://localhost:8000/events/oauth/callback/"
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

    return redirect('users:vendor_dashboard')

@login_required
def book_appointment(request, package_id):
    """Handles the appointment booking for a vendor package"""
    package = get_object_or_404(VendorPackage, id=package_id)

    if request.method == "GET":
        # Render the calendar page
        return render(request, 'events/book_appointment.html', {'package': package})

    elif request.method == "POST":
        data = json.loads(request.body)
        selected_date = data.get("date")

        if not selected_date:
            return JsonResponse({"error": "No date provided"}, status=400)

        # Check if the package is already booked for the selected date
        existing_booking = VendorEvent.objects.filter(
            vendor=package.vendor, vendor_package=package, event_date=selected_date
        ).exists()

        if existing_booking:
            return JsonResponse({"error": "This slot is already booked"}, status=400)

        # Create the appointment
        new_event = VendorEvent.objects.create(
            vendor=package.vendor,
            vendor_package=package,
            customer_name=request.user.customer_name,
            email=request.user.email,
            customer_user=request.user,
            contact_no=request.user.contact_no,
            event_name=f"Booking for {package.pkg_name}",
            event_date=selected_date,
            event_state="on_hold"
        )

        send_event_emails(
            vendor=package.vendor,
            customer_email=request.user.email,
            customer_name=request.user.customer_name,
            event_name=f"Booking for {package.pkg_name}",
            event_date=selected_date,
            package_name=package.pkg_name
        )

        return JsonResponse({"success": True, "redirect_url": "/events/bookings/list/"})

    return JsonResponse({"error": "Invalid request"}, status=400)

def send_event_emails(vendor, customer_email, customer_name, event_name, event_date, package_name):
    # 1. Email to Vendor
    vendor_subject = "New Booking Notification"
    vendor_html = render_to_string('events/vendor_event_email.html', {
        'vendor_name': vendor.business_name,
        'event_name': event_name,
        'event_date': event_date,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'contact_no': vendor.contact_no,
    })

    vendor_email = EmailMultiAlternatives(
        subject=vendor_subject,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[vendor.user.email],
    )
    vendor_email.attach_alternative(vendor_html, "text/html")
    vendor_email.send()

    # 2. Email to Customer
    customer_subject = "Booking Confirmation"
    customer_html = render_to_string('events/customer_event_email.html', {
        'customer_name': customer_name,
        'vendor_name': vendor.business_name,
        'package_name': package_name,
        'event_date': event_date,
    })

    customer_email_obj = EmailMultiAlternatives(
        subject=customer_subject,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer_email],
    )
    customer_email_obj.attach_alternative(customer_html, "text/html")
    customer_email_obj.send()