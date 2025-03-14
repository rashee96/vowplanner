from django import forms
from .models import VendorPackage


class VendorPackageForm(forms.ModelForm):
    class Meta:
        model = VendorPackage
        fields = ['pkg_name', 'pkg_description', 'images', 'pkg_price']
        widgets = {
            'pkg_name': forms.TextInput(attrs={'class': 'form-control'}),
            'pkg_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'pkg_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }