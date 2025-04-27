from django import forms
from .models import Quotation, QuotationLine


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['discount', 'total_price', 'net_total', 'status', 'payment_method']

    def clean_total_price(self):
        total_price = self.cleaned_data.get('total_price')
        if total_price is None:
            raise forms.ValidationError("Total price is required.")
        return total_price

    def clean_net_total(self):
        net_total = self.cleaned_data.get('net_total')
        if net_total is None:
            raise forms.ValidationError("Net total is required.")
        return net_total

class QuotationLineForm(forms.ModelForm):
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control w-50 mx-auto'}))

    class Meta:
        model = QuotationLine
        fields = ['description', 'price']