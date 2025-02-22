from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'customer_name', 'vendor_name','username', 'email', 'user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('user_type', 'is_staff', 'is_active')

admin.site.register(CustomUser, CustomUserAdmin)
