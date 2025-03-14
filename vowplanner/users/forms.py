from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Vendor

class CustomerRegistrationForm(UserCreationForm):
    customer_name = forms.CharField(
        max_length=255,
        required=True,
        label="Customer Name",
        help_text="Enter your full name."
    )

    password1 = forms.CharField(
        label="Password",  
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    password2 = forms.CharField(
        label="Confirm Password",  
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = CustomUser
        fields = ['customer_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class VendorRegistrationForm(UserCreationForm):
    BUSINESS_CATEGORIES = [
        ('Venues', 'Venues'),
        ('Photography', 'Photography'),
        ('Videography', 'Videography'),
        ('Wedding_favors', 'Wedding Favors'),
        ('Wedding_cake', 'Wedding Cake'),
    ]
    vendor_name = forms.CharField(
        max_length=255,
        required=True,
        label="Vendor Name",
        help_text="Enter your name."
    )

    business_name = forms.CharField(max_length=255, required=True, help_text="Enter your business name")
    business_category = forms.ChoiceField(
        choices=BUSINESS_CATEGORIES,
        required=True,
        label="Business Category"
    )
    contact_no = forms.CharField(max_length=15, required=True, help_text="Enter your contact number")

    password1 = forms.CharField(
        label="Password",  
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    password2 = forms.CharField(
        label="Confirm Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = CustomUser
        fields = ['vendor_name', 'username', 'email', 'business_name', 'business_category', 'contact_no', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'vendor'  
        if commit:
            user.save()

            Vendor.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name'],
                business_category=self.cleaned_data['business_category'],
                contact_no=self.cleaned_data['contact_no']
            )
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
