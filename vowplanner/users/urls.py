from django.urls import path
from .views import (customer_register, forgot_password, vendor_register, user_login, user_logout,
                    home, vendor_dashboard, create_vendor_package, update_vendor_package,
                    archive_vendor_package, category_packages)

urlpatterns = [
    path('', home, name='home'),
    path('register/customer/', customer_register, name='customer_register'),
    path('register/vendor/', vendor_register, name='vendor_register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('vendor/dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('vendor/package/create/', create_vendor_package, name='create_vendor_package'),
    path('vendor/package/update/<int:package_id>/', update_vendor_package,
         name='update_vendor_package'),
    path('vendor/package/archive/<int:package_id>/', archive_vendor_package,
         name='archive_vendor_package'),
    path('category/<str:category>/', category_packages, name='category_packages'),
]
