from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment



class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
 
 
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
 
 
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    #your fields here
    inlines       = [InvoiceItemInline, PaymentInline]