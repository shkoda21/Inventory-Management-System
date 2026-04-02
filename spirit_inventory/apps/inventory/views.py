"""
Public portfolio version of inventory views.

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
from django.db.models import Q, Count, Max
from django.core.paginator import Paginator
from django.db import transaction
import json

from .models import Capacity, TypeLiqueur, Barcode, Batch, Ingredient, Product, Retailer
from .forms import (
    CapacityForm, TypeLiqueurForm, BarcodeForm, BatchForm,
    IngredientForm, ProductForm, ProductUpdateForm,
    RetailerForm, BatchFilterForm, ProductFilterForm, RetailerFilterForm, BarcodeFilterForm, TypeFilterForm,
)
from apps.accounts.permissions import write_required, supervisor_required
from apps.audit.helpers import log_action, get_changes
from apps.audit.models import AuditLog

# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Simplified dashboard view.

    Production version includes:
    - low stock detection
    - operational analytics
    - recent transactions
    """
    context = {
        "total_products": Product.objects.count(),
        "total_batches": Batch.objects.count(),
        "total_retailers": Retailer.objects.count(),
    }
    return render(request, "inventory/dashboard.html", context)


# ── Capacity ──────────────────────────────────────────────────────────────────

@login_required
def capacity_list(request):
    qs = Capacity.objects.annotate(product_count=Count('products'))
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, 'inventory/capacity_list.html', {
        'capacities': qs, 'form': CapacityForm(), 'q': q,
    })


@login_required
@write_required
def capacity_save(request, pk=None):
    """
    Simplified create/update view.
    """
    instance = get_object_or_404(Capacity, pk=pk) if pk else None

    if request.method == 'POST':
        form = CapacityForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()

            # Hidden in public version
            # log_action(...)

            return redirect('inventory:capacity_list')

    return redirect('inventory:capacity_list')


@login_required
@supervisor_required
def capacity_delete(request, pk):
    capacity = get_object_or_404(Capacity, pk=pk)
    if request.method == 'POST':
        if capacity.products.exists():
            messages.error(request, f'Cannot delete — products use this capacity.')
        else:
            log_action(request, AuditLog.ACTION_DELETE, capacity)
            capacity.delete()
            messages.success(request, f'Capacity "{capacity.name}" deleted.')
        return redirect('inventory:capacity_list')
    return render(request, 'inventory/confirm_delete.html', {
        'object': capacity, 'object_type': 'Capacity', 'back_url': 'inventory:capacity_list',
    })


# ── TypeLiqueur ───────────────────────────────────────────────────────────────

@login_required
def type_list(request):
    types = TypeLiqueur.objects.all()
    return render(request, "inventory/type_list.html", {
        "types": types,
        "form": TypeLiqueurForm(),
    })


@login_required
@write_required
def type_save(request, pk=None):
    instance = get_object_or_404(TypeLiqueur, pk=pk) if pk else None

    if request.method == "POST":
        form = TypeLiqueurForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    return redirect("inventory:type_list")


@login_required
@supervisor_required
def type_delete(request, pk):
    obj = get_object_or_404(TypeLiqueur, pk=pk)

    if request.method == "POST":
        obj.delete()
        return redirect("inventory:type_list")

    return render(request, "inventory/confirm_delete.html", {"object": obj})


# ── Barcode ───────────────────────────────────────────────────────────────────

@login_required
def barcode_list(request):
    qs = Barcode.objects.all()
    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))

    return render(request, "inventory/barcode_list.html", {
        "page_obj": page_obj,
        "form": BarcodeForm(),
    })


@login_required
@write_required
def barcode_save(request, pk=None):
    instance = get_object_or_404(Barcode, pk=pk) if pk else None

    if request.method == "POST":
        form = BarcodeForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()

    return redirect("inventory:barcode_list")


@login_required
@supervisor_required
def barcode_delete(request, pk):
    obj = get_object_or_404(Barcode, pk=pk)

    if request.method == "POST":
        obj.delete()
        return redirect("inventory:barcode_list")

    return render(request, "inventory/confirm_delete.html", {"object": obj})


# ── Batch ─────────────────────────────────────────────────────────────────────

@login_required
def batch_list(request):
    qs = Batch.objects.all()
    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))

    return render(request, "inventory/batch_list.html", {
        "page_obj": page_obj,
    })


@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    products = Product.objects.filter(batch=batch)

    return render(request, "inventory/batch_detail.html", {
        "batch": batch,
        "products": products,
    })


@login_required
@write_required
def batch_create(request):
    form = BatchForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        batch = form.save()
        return redirect("inventory:batch_detail", pk=batch.pk)

    return render(request, "inventory/batch_form.html", {"form": form})


@login_required
@write_required
def batch_update(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    form = BatchForm(request.POST or None, instance=batch)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory:batch_detail", pk=pk)

    return render(request, "inventory/batch_form.html", {
        "form": form,
        "batch": batch,
    })


@login_required
@supervisor_required
def batch_delete(request, pk):
    batch = get_object_or_404(Batch, pk=pk)

    if request.method == "POST":
        batch.delete()
        return redirect("inventory:batch_list")

    return render(request, "inventory/confirm_delete.html", {"object": batch})

# ── Ingredients (AJAX) ────────────────────────────────────────────────────────

def _json_to_querydict(data):
    """
    Convert a plain dict (from json.loads) to a QueryDict.
    Django form fields expect string input — same as a real HTML POST.
    Passing a plain dict with native Python types (int, float) causes
    DecimalField and other typed fields to fail validation silently.
    """
    from django.http import QueryDict
    return qd

@login_required
@write_required
def ingredient_add(request, batch_pk):
    """
    AJAX endpoint (simplified).

    Full implementation removed in public version.
    """
    return JsonResponse({'success': True})

# ── Product ───────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
    qs = Product.objects.all()
    page_obj = Paginator(qs, 50).get_page(request.GET.get("page"))

    return render(request, "inventory/product_list.html", {
        "page_obj": page_obj,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, "inventory/product_detail.html", {
        "product": product,
    })


@login_required
@write_required
def product_create(request):
    """
    Simplified product creation.

    Production version includes:
    - batch-aware bottle numbering
    - transactional creation
    - validation rules
    """
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory:product_list")

    return render(request, "inventory/product_form.html", {"form": form})


@login_required
@write_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductUpdateForm(request.POST or None, instance=product)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory:product_detail", pk=pk)

    return render(request, "inventory/product_form.html", {
        "form": form,
        "product": product,
    })


@login_required
@supervisor_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("inventory:product_list")

    return render(request, "inventory/confirm_delete.html", {"object": product})


# ── Retailer ──────────────────────────────────────────────────────────────────

@login_required
def retailer_list(request):
    qs = Retailer.objects.all()
    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))

    return render(request, "inventory/retailer_list.html", {
        "page_obj": page_obj,
    })


@login_required
def retailer_detail(request, pk):
    retailer = get_object_or_404(Retailer, pk=pk)

    return render(request, "inventory/retailer_detail.html", {
        "retailer": retailer,
    })


@login_required
@write_required
def retailer_create(request):
    form = RetailerForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        retailer = form.save()
        return redirect("inventory:retailer_detail", pk=retailer.pk)

    return render(request, "inventory/retailer_form.html", {"form": form})


@login_required
@write_required
def retailer_update(request, pk):
    retailer = get_object_or_404(Retailer, pk=pk)
    form = RetailerForm(request.POST or None, instance=retailer)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory:retailer_detail", pk=pk)

    return render(request, "inventory/retailer_form.html", {
        "form": form,
        "retailer": retailer,
    })


@login_required
@supervisor_required
def retailer_delete(request, pk):
    retailer = get_object_or_404(Retailer, pk=pk)

    if request.method == "POST":
        retailer.delete()
        return redirect("inventory:retailer_list")

    return render(request, "inventory/confirm_delete.html", {"object": retailer})

@login_required
def retailer_autocomplete(request):
    q = request.GET.get('q', '').strip()
    # In production, this would include more complex logic to handle store vs org names,
    # and would likely be optimized with a dedicated search backend.
    return JsonResponse(data, safe=False)
