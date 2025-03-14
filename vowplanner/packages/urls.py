from django.urls import path
from . import views

app_name = 'packages'
urlpatterns = [
    path('vendor-packages/', views.all_vendor_packages, name='all_vendor_packages'),
    path('<int:package_id>/get_availability/', views.get_vendor_availability,
         name='get_vendor_availability'),
    path('create/', views.create_vendor_package, name='create_vendor_package'),
    path('update/<int:package_id>/', views.update_vendor_package,
         name='update_vendor_package'),
    path('category/<str:category>/', views.category_packages, name='category_packages'),
    path('<int:package_id>/', views.package_detail, name='package_detail'),
    path('archive/<int:package_id>/', views.archive_vendor_package,
         name='archive_vendor_package')
]
