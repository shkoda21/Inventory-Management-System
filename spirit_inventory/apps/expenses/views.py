from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from collections import defaultdict
import json

from .models import Expense
from .forms import ExpenseForm, ExpenseFilterForm
from apps.accounts.permissions import write_required, supervisor_required, export_required
from apps.audit.helpers import log_action
from apps.audit.models import AuditLog


def _apply_filters(qs, form):
    if not form.is_valid():
        return qs
    cd = form.cleaned_data
    # Add filtering logic based on form fields
    return qs


@login_required
def expense_list(request):
    from apps.accounts.permissions import ExpenseViewMixin
    if not request.user.can_view_expenses:
        from django.contrib import messages
        messages.error(request, "You don't have permission to view expenses.")
        return redirect('inventory:dashboard')

    form = ExpenseFilterForm(request.GET)
    qs = _apply_filters(Expense.objects.all(), form)
    total = qs.aggregate(s=Sum('total_price'))['s'] or 0

    # Chart data by type
    TYPE_COLORS = {
        'ingredients': '#1a3a52',
        'equipment':   '#2e6d9e',
        'packaging':   '#4a90d9',
        'rent':        '#5b8e6e',
        'office':      '#f0a500',
        'marketing':   '#e06c1a',
        'taxes':       '#9b3d8f',
        'labor':       '#3d6b4f',
        'Internet':    "#f0e462",
        'other':       '#7b7b7b',
    }
    TYPE_DISPLAY = dict(Expense.TYPE_CHOICES)

    # Chart data by type — use display names for labels, matched colors
    by_type = list(qs.values('type').annotate(total=Sum('total_price')).order_by('-total'))
    chart_type = {
        'labels': [TYPE_DISPLAY.get(e['type'], e['type']) for e in by_type],
        'data':   [float(e['total']) for e in by_type],
        'colors': [TYPE_COLORS.get(e['type'], '#999') for e in by_type],
    }

    # Chart data by date
    date_totals = defaultdict(float)
    for exp in qs:
        if exp.date_purchase:
            date_totals[str(exp.date_purchase)] += float(exp.total_price)
    sorted_dates = sorted(date_totals.items())
    chart_date = {'labels': [d for d, _ in sorted_dates], 'data': [v for _, v in sorted_dates]}

    page_obj = Paginator(qs, 30).get_page(request.GET.get('page'))
    return render(request, 'expenses/expense_list.html', {
        'page_obj': page_obj, 'form': form,
        'total': total, 'count': qs.count(),
        'chart_type': json.dumps(chart_type),
        'chart_date': json.dumps(chart_date),
    })


@login_required
def expense_detail(request, pk):
    if not request.user.can_view_expenses:
        return redirect('inventory:dashboard')
    expense = get_object_or_404(Expense, pk=pk)
    return render(request, 'expenses/expense_detail.html', {'expense': expense})


@login_required
@write_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        expense = form.save()
        log_action(request, AuditLog.ACTION_CREATE, expense)
        messages.success(request, f'Expense "{expense.name}" created.')
        return redirect('expenses:expense_detail', pk=expense.pk)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'New Expense'})


@login_required
@write_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        updated = form.save()
        log_action(request, AuditLog.ACTION_UPDATE, updated)
        messages.success(request, f'Expense "{expense.name}" updated.')
        return redirect('expenses:expense_detail', pk=pk)
    return render(request, 'expenses/expense_form.html', {
        'form': form, 'expense': expense, 'title': f'Edit — {expense.name}',
    })


@login_required
@supervisor_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        log_action(request, AuditLog.ACTION_DELETE, expense)
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expenses:expense_list')
    return render(request, 'expenses/confirm_delete.html', {
        'object': expense, 'object_type': 'Expense',
        'back_url': 'expenses:expense_detail', 'back_pk': pk,
    })