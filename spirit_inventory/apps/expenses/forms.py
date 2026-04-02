from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["your fields here"]  # Replace with actual fields from the Expense model
        widgets = {
            "Replace with field name": forms.TextInput(attrs={"class": "form-control"}),
            # Add widgets for other fields as needed
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logic to dynamically adjust fields based on type can be added here

    def clean_date_purchase(self):
        # Ensure the purchase date is not in the future
        return d


class ExpenseFilterForm(forms.Form):
    # This form can be used to filter expenses in the list view