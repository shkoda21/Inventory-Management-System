from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import SellOrder, ReturnOrder, WriteOff
from apps.inventory.models import Batch, Capacity, TypeLiqueur, Retailer


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, (forms.TextInput, forms.NumberInput, forms.EmailInput,
                               forms.Textarea, forms.DateInput, forms.PasswordInput)):
                w.attrs.setdefault('class', 'form-control')
            elif isinstance(w, forms.Select):
                w.attrs.setdefault('class', 'form-select')
            elif isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault('class', 'form-check-input')


# ── Sell Order ────────────────────────────────────────────────────────────────

class SellOrderForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = SellOrder
        fields = ['retailer', 'sell_date', 'extra_notice']
        widgets = {
            'sell_date':    forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'extra_notice': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'retailer':     forms.HiddenInput(),  # set via autocomplete JS
        }

    def clean_sell_date(self):
        d = self.cleaned_data.get('sell_date')
        if d and d > timezone.now().date():
            raise ValidationError('Sell date cannot be in the future.')
        return d


class ProductFilterForSellForm(forms.Form):
    """Filter available (in-stock) products when building a sell order."""
    #your filter fields here, e.g.

class AddGroupBottlesForm(forms.Form):
    """Bulk-add a range of bottle numbers from a batch+capacity to a sell order."""
    
# ── Sell Order Filter ─────────────────────────────────────────────────────────


# ── Return Order ──────────────────────────────────────────────────────────────

class ReturnOrderForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ReturnOrder
        fields = ['sell_order', 'date_return', 'extra_notice']
        widgets = {
            'sell_order':   forms.Select(attrs={'class': 'form-select'}),
            'date_return':  forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'extra_notice': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def clean(self):
        cd = super().clean()
        date_return = cd.get('date_return')
        sell_order  = cd.get('sell_order')
        if date_return:
            if date_return > timezone.now().date():
                self.add_error('date_return', 'Return date cannot be in the future.')
            if sell_order and date_return < sell_order.sell_date:
                self.add_error(
                    'date_return',
                    f'Return date cannot be before the sell date ({sell_order.sell_date}).'
                )
        return cd


class ReturnOrderFilterForm(forms.Form):
    # your filter fields here


class ProductFilterForReturnForm(forms.Form):
    """Filter products from a specific sell order that can be returned."""

# ── Write-off ─────────────────────────────────────────────────────────────────

class WriteOffForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = WriteOff
        fields = ['reason_category', 'reason', 'price_cost', 'date_write_off', 'extra_notice']
        widgets = {
            'reason':       forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'extra_notice': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'date_write_off': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_date_write_off(self):
        d = self.cleaned_data.get('date_write_off')
        if d and d > timezone.now().date():
            raise ValidationError('Write-off date cannot be in the future.')
        return d


class WriteOffUpdateForm(BootstrapMixin, forms.ModelForm):
    """Update — product is read-only, only metadata can change."""

class WriteOffFilterForCreateForm(forms.Form):
    """Filter in-stock products when selecting bottles to write off."""
    
class WriteOffListFilterForm(forms.Form):
    # your filter fields here