from django.urls import path
from . import views

app_name = 'events'
urlpatterns = [
    path("get_all_events/", views.get_all_events, name="get_all_events"),
    path("create_event/", views.create_event, name="create_event"),
    path("delete_google_event/", views.delete_google_calendar_event,
         name="delete_google_calendar_event"),
    path("clear_google_credentials/", views.clear_google_credentials,
         name="clear_google_credentials"),

    path('bookings/list/', views.user_booking_list, name='user_booking_list'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path("fetch_and_save_google_events/", views.fetch_and_save_google_events,
         name="fetch_and_save_google_events"),
    path("oauth/", views.google_auth, name="google_auth"),
    path("oauth/callback/", views.google_auth_callback, name="google_auth_callback"),
    path('<int:package_id>/book/', views.book_appointment, name='book_appointment'),
]
