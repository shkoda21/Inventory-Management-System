from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Capacity, TypeLiqueur, Barcode, Batch, Ingredient, Product, Retailer
import datetime


# ── Mixins ─────────────────────────────────────────────────────────────────

class BootstrapMixin:
    """Auto-applies Bootstrap classes to all fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.NumberInput,
                                   forms.EmailInput, forms.URLInput,
                                   forms.PasswordInput, forms.Textarea,
                                   forms.DateInput)):
                widget.attrs.setdefault('class', 'form-control')
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')


class DateValidationMixin:
    # Optional mixin to validate that a date field is not in the future.
    date_field = None

    def clean(self):
        return cleaned_data


#Add your forms here. Use the mixins above for consistent styling and validation across forms.

"""Example ── Batch Forms ─────────────────────────────────────────────────────────────

class BatchForm(BootstrapMixin, DateValidationMixin, forms.ModelForm):
    date_field = 'start_date'

    class Meta:
        model = Batch
        fields = [
            'name', 'type', 'alcohol_volume',
            #additional fields from the model can be added as needed, e.g. start_date, end_date, volume, etc.
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date':   forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        help_texts = {
            'alcohol_volume': 'Alcohol by volume %, e.g. 40.00 for 40%.',
            'volume': 'Total batch volume in liters.',
        }

    def clean(self):
        return cleaned_data """


# ──Add your Filter Forms ────────────────────────────────────────────────────────────

"""Example ── Batch Filter Form ─────────────────────────────────────────────────────"""
class BatchFilterForm(forms.Form):
    q          = forms.CharField(required=False, label='Search',
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Batch name...'}))
    type       = forms.ModelChoiceField(queryset=TypeLiqueur.objects.all(), required=False, empty_label='All types',
                    widget=forms.Select(attrs={'class': 'form-select'}))
    date_start = forms.DateField(required=False, label='From',
                    widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_end   = forms.DateField(required=False, label='To',
                    widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

