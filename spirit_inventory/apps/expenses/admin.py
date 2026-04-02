from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['your fields here']  # Replace with actual fields from the Expense model
    list_filter  = ['your fields here']
    search_fields = ['your fields here']