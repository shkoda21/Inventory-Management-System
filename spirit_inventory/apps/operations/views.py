"""
Public portfolio version of operations views.

NOTE:
This module is intentionally simplified.

The production system includes:
- advanced filtering and aggregation
- transactional operations
- audit logging
- complex business rules (inventory lifecycle, reporting)

These have been removed to protect proprietary logic
while preserving overall architecture and structure.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, F
from django.core.paginator import Paginator
from django.db import transaction
from django.template.loader import render_to_string
import json
 
from .models import SellOrder, SellItem, ReturnOrder, ReturnItem, WriteOff
from .forms import (
    SellOrderForm, ProductFilterForSellForm, AddGroupBottlesForm,
    SellOrderFilterForm, ReturnOrderForm, ReturnOrderFilterForm,
    ProductFilterForReturnForm, WriteOffForm, WriteOffUpdateForm,
    WriteOffFilterForCreateForm, WriteOffListFilterForm,
)
from apps.inventory.models import Product, Batch, Capacity, TypeLiqueur
from apps.accounts.permissions import write_required, supervisor_required
from apps.audit.helpers import log_action
from apps.audit.models import AuditLog
 


# ── Helpers ───────────────────────────────────────────────────────────────────

def _filter_products_for_sell(qs, form, sell_date=None):
    qs = qs.filter(in_stock=True)
    # your filter logic here
    return qs


def _filter_sell_orders(qs, form):
    if not form.is_valid():
        #your filter logic here
    return qs


# ── Sell Order List ───────────────────────────────────────────────────────────

@login_required
def sell_order_list(request):
    from django.db.models import OuterRef, Subquery, DecimalField as DField
    from apps.invoices.models import Payment
 
    form = SellOrderFilterForm(request.GET)
    qs = SellOrder.objects.select_related('retailer').prefetch_related('return_orders')
    qs = _filter_sell_orders(qs, form).order_by('-sell_date', '-pk')
 
    # Filter by payment status — annotate with paid_amount then compare to total
    if form.is_valid():
        #your code is here
 
    #calculate totals for footer
    # NOTE: in production, these are calculated with more complex logic that accounts for returns, write-offs, etc. 
    page_obj = Paginator(qs, 30).get_page(request.GET.get('page'))
    return render(request, 'operations/sell_order_list.html', {
        'page_obj': page_obj, 'form': form,
        'total': qs.count(),
        'total_revenue': total_revenue,
        'total_returns': total_returns,
        'net_profit': total_revenue - total_returns,
    })

# ── Sell Order Create / Update ────────────────────────────────────────────────

@login_required
@write_required
def sell_order_form(request, pk=None):
    order = get_object_or_404(SellOrder, pk=pk) if pk else None
    filter_form = ProductFilterForSellForm(request.GET or None)
    group_form  = AddGroupBottlesForm()

    # Handle sell order header save (POST with retailer + date)

    # Filtered product list

    # AJAX product list refresh

    return render(request, 'operations/sell_order_form.html', {
        'order': order,
        'order_form': order_form,
        'filter_form': filter_form,
        'group_form': group_form,
        'products': products,
        'items': items,
    })


# ── Sell Order Detail ─────────────────────────────────────────────────────────

@login_required
def sell_order_detail(request, pk):
    order = get_object_or_404(
        SellOrder.objects.select_related('retailer')
                         .prefetch_related('items__product__batch__type',
                                           'items__product__capacity',
                                           'return_orders'),
        pk=pk,
    )
    referer  = request.META.get('HTTP_REFERER', '')
    back_url = referer if referer else None
    return render(request, 'operations/sell_order_detail.html', {'order': order, 'back_url': back_url})

# ── Sell Order Delete ─────────────────────────────────────────────────────────

@login_required
@supervisor_required
def sell_order_delete(request, pk):
    order = get_object_or_404(SellOrder, pk=pk)
    if request.method == 'POST':
        if order.return_orders.exists():
            messages.error(request, 'Cannot delete — this order has return orders.')
            return redirect('operations:sell_order_detail', pk=pk)
        with transaction.atomic():
            for item in order.items.all():
                item.product.in_stock = True
                item.product.save(update_fields=['in_stock'])
            log_action(request, AuditLog.ACTION_DELETE, order)
            order.delete()
        messages.success(request, 'Sell order deleted.')
        return redirect('operations:sell_order_list')
    return render(request, 'operations/confirm_delete.html', {
        'object': order, 'object_type': 'Sell Order',
        'back_url': 'operations:sell_order_detail', 'back_pk': pk,
    })


# ── Add / Remove single bottle (AJAX) ────────────────────────────────────────

@login_required
@write_required
def sell_item_add(request, order_pk, product_pk):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    order   = get_object_or_404(SellOrder, pk=order_pk)
    product = get_object_or_404(Product, pk=product_pk)
    try:
        with transaction.atomic():
            order.add_item(product)
            log_action(request, AuditLog.ACTION_UPDATE, order,
                       changes={'bottle_added': ['', str(product)]})
        items_html = render_to_string('operations/partials/sell_items_list.html',
                                      {'items': order.items.select_related(
                                          'product__batch__type', 'product__capacity').all(),
                                       'order': order}, request=request)
        return JsonResponse({
            'success': True,
            'items_html': items_html,
            'total': str(order.total_price),
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@write_required
def sell_item_remove(request, order_pk, product_pk):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    order   = get_object_or_404(SellOrder, pk=order_pk)
    product = get_object_or_404(Product, pk=product_pk)
    try:
        with transaction.atomic():
            order.remove_item(product)
            log_action(request, AuditLog.ACTION_UPDATE, order,
                       changes={'bottle_removed': [str(product), '']})
        items_html = render_to_string('operations/partials/sell_items_list.html',
                                      {'items': order.items.select_related(
                                          'product__batch__type', 'product__capacity').all(),
                                       'order': order}, request=request)
        return JsonResponse({
            'success': True,
            'items_html': items_html,
            'total': str(order.total_price),
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ── Update item price (AJAX) ──────────────────────────────────────────────────

@login_required
@write_required
def sell_item_price_update(request, order_pk):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    try:
        data       = json.loads(request.body)
        product_pk = data.get('product_id')
        new_price  = data.get('price')
        from decimal import Decimal
        item = get_object_or_404(SellItem, order_id=order_pk, product_id=product_pk)
        item.price = Decimal(str(new_price))
        item.save(update_fields=['price'])
        item.order.update_total()
        return JsonResponse({'success': True, 'total': str(item.order.total_price)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ── Bulk add bottles (AJAX) ───────────────────────────────────────────────────

@login_required
@write_required
def sell_items_bulk_add(request, order_pk):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    order = get_object_or_404(SellOrder, pk=order_pk)
    form  = AddGroupBottlesForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    cd = form.cleaned_data
    products = Product.objects.filter(
        batch=cd['batch'],
        capacity=cd['capacity'],
        bottle_number__range=(cd['bottle_from'], cd['bottle_to']),
        in_stock=True,
        production_date__lte=order.sell_date,
    )
    added, skipped = [], []
    with transaction.atomic():
        for product in products:
            try:
                order.add_item(product)
                added.append(product.pk)
            except ValueError as e:
                skipped.append(str(e))
    log_action(request, AuditLog.ACTION_UPDATE, order,
               changes={'bulk_added': [0, len(added)]})
    items_html = render_to_string('operations/partials/sell_items_list.html',
                                  {'items': order.items.select_related(
                                      'product__batch__type', 'product__capacity').all(),
                                   'order': order}, request=request)
    return JsonResponse({
        'success': True,
        'added': len(added),
        'skipped': len(skipped),
        'items_html': items_html,
        'total': str(order.total_price),
    })


# ── Sell order search (for return order dropdown) ─────────────────────────────

@login_required
def sell_order_search(request):
    q = request.GET.get('q', '').strip()
    qs = SellOrder.objects.filter(
        Q(pk__icontains=q) |
        Q(retailer__organization_name__icontains=q) |
        Q(retailer__store_name__icontains=q)
    ).select_related('retailer')[:15]
    return JsonResponse([{
        'id': o.pk,
        'text': f"#{o.pk} — {o.retailer} — {o.sell_date}",
    } for o in qs], safe=False)


# ── Return Order List ─────────────────────────────────────────────────────────

@login_required
def return_order_list(request):
    #your code here
    return render(request, 'operations/return_order_list.html')


# ── Return Order Create / Update ──────────────────────────────────────────────

# ── Return Order Detail ───────────────────────────────────────────────────────

# ── Return Order Delete ───────────────────────────────────────────────────────

# ── Return Item Add / Remove (AJAX) ───────────────────────────────────────────

# ── Write-off: Select Products ────────────────────────────────────────────────

# ── Write-off: Confirm & Execute ──────────────────────────────────────────────

# ── Write-off List ────────────────────────────────────────────────────────────

# ── Write-off Detail / Update / Delete ───────────────────────────────────────
