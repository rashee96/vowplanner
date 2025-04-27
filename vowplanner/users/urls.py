from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.home, name='home'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/vendor/', views.vendor_register, name='vendor_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password_request'),
    path('reset-password/<uidb64>/', views.reset_password, name='reset_password'),
]
