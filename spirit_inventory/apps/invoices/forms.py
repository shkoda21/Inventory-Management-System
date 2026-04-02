from django import forms
from .models import Invoice, InvoiceItem, Payment

PAYMENT_STATUS_CHOICES = [
    #your choice values should be empty string for "All", and "paid" for "Paid"
]


class InvoiceGenerateForm(forms.Form):
    """Shown when generating invoice from a sell order."""


class InvoiceFilterForm(forms.Form):
    #your filter fields

class PaymentForm(forms.ModelForm):
    class Meta:
        model   = Payment
        fields  = ["your fields here"]
        widgets = {
            #your widgets here
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product_name', 'capacity', 'qty', 'unit_price']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity':     forms.TextInput(attrs={'class': 'form-control'}),
            'qty':          forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price':   forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }