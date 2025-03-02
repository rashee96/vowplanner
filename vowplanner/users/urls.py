from django.urls import path
from .views import (customer_register, forgot_password, package_detail, save_unavailable_dates,
                    vendor_register, user_login, user_logout,
                    home, vendor_dashboard, create_vendor_package, update_vendor_package,
                    archive_vendor_package, category_packages, google_auth, google_auth_callback,
                    fetch_google_calendar_events, add_google_calendar_event,
                    delete_google_calendar_event, clear_google_credentials)

urlpatterns = [
    path('', home, name='home'),
    path('register/customer/', customer_register, name='customer_register'),
    path('register/vendor/', vendor_register, name='vendor_register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('vendor/dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('vendor/package/create/', create_vendor_package, name='create_vendor_package'),
    path('vendor/package/update/<int:package_id>/', update_vendor_package,
         name='update_vendor_package'),
    path('category/<str:category>/', category_packages, name='category_packages'),
    path('package/<int:package_id>/', package_detail, name='package_detail'),
    path('vendor/package/archive/<int:package_id>/', archive_vendor_package,
         name='archive_vendor_package'),
    path("save-unavailable-dates/", save_unavailable_dates, name="save_unavailable_dates"),
    path("oauth/", google_auth, name="google_auth"),
    path("oauth/callback/", google_auth_callback, name="google_auth_callback"),
    path("fetch_google_events/", fetch_google_calendar_events, name="fetch_google_calendar_events"),
    path("add_google_event/", add_google_calendar_event, name="add_google_calendar_event"),
    path("delete_google_event/", delete_google_calendar_event, name="delete_google_calendar_event"),
    path("clear_google_credentials/", clear_google_credentials, name="clear_google_credentials"),

]
