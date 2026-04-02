from django import forms
from apps.inventory.models import TypeLiqueur, Capacity, Retailer


class TTBFilterForm(forms.Form):
    date_start = forms.DateField(
        required=False, label='From',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    date_end = forms.DateField(
        required=False, label='To',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    type = forms.ModelChoiceField(
        queryset=TypeLiqueur.objects.all(), required=False, empty_label='All types',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    capacity = forms.ModelChoiceField(
        queryset=Capacity.objects.all(), required=False, empty_label='All sizes',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    retailer = forms.ModelChoiceField(
        queryset=Retailer.objects.all(), required=False, empty_label='All retailers',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class AnalysisFilterForm(forms.Form):
    date_start = forms.DateField(
        required=False, label='From',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    date_end = forms.DateField(
        required=False, label='To',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )