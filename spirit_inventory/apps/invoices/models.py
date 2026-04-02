from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime

from apps.inventory.models import Retailer
from apps.operations.models import SellOrder, SellItem


class Invoice(models.Model):
    """
    Customer-facing document generated from a SellOrder.
    Aggregates individual bottle records into line items by type + capacity.

    Key design decisions:
    - Snapshot fields freeze org data at creation time (legal requirement)
    - No direct FK to individual Product instances — only to Retailer and SellOrder
    - bottle_numbers are intentionally excluded from the invoice
    """
    # --- Link to source data ---
    sell_order = models.OneToOneField(
        SellOrder,
        on_delete=models.PROTECT,
        related_name='invoice',
        null=True,
        blank=True,
        help_text='The sell order this invoice was generated from.',
    )
    retailer = models.ForeignKey(
        Retailer,
        on_delete=models.PROTECT,
        related_name='invoices',
    )

    # --- Auto-generated invoice number ---
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)

    # --- Snapshot fields: frozen at invoice creation ---
    # These must never change even if retailer data is updated later
    org_name_snapshot     = models.CharField(max_length=255)
    license_snapshot      = models.CharField(max_length=100)
    org_address_snapshot  = models.TextField()

    # Store fields — stored but NOT shown on exported invoice
    store_name_snapshot    = models.CharField(max_length=255, blank=True)
    store_address_snapshot = models.TextField(blank=True)

    # --- Invoice data ---
    date     = models.DateField()
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    extra_notice = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-pk']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['retailer']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number}"

    def get_absolute_url(self):
        return reverse('invoices:invoice_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        # Snapshot retailer data on first save
        if not self.pk:
            self._snapshot_retailer()
            super().save(*args, **kwargs)
            # Auto-generate invoice number after pk is assigned
            year = datetime.now().year
            self.invoice_number = f"INV-{year}-{self.pk:05d}"
            Invoice.objects.filter(pk=self.pk).update(invoice_number=self.invoice_number)
        else:
            super().save(*args, **kwargs)

    def _snapshot_retailer(self):
        """Freeze retailer data at invoice creation time."""
        r = self.retailer
        self.org_name_snapshot    = r.organization_name
        self.license_snapshot     = r.license
        self.org_address_snapshot = r.organization_address
        self.store_name_snapshot  = r.store_name
        self.store_address_snapshot = r.store_address

    def subtotal(self):
        return self.items.aggregate(
            s=Sum(models.F('qty') * models.F('unit_price'),
                  output_field=models.DecimalField())
        )['s'] or Decimal('0.00')

    def calculate_total(self):
        return self.subtotal() - self.discount

    def update_total(self):
        self.total_amount = self.calculate_total()
        Invoice.objects.filter(pk=self.pk).update(total_amount=self.total_amount)

    #Add your @property methods for payment status ───────────────────────────────────────────────────────

    
    @classmethod
    def generate_from_sell_order(cls, sell_order, discount=Decimal('0.00'), extra_notice=''):
        """
        Create an Invoice with aggregated InvoiceItems from a SellOrder.

        Groups SellItems by (type_name, capacity_name, price) and sums qty.
        Bottle numbers are intentionally excluded — invoices never show them.
        """
        # your code to generate invoice from sell order here
        
        return invoice


class InvoiceItem(models.Model):
    """
    One line on an invoice. Represents an aggregated group of bottles
    (same type, same capacity, same price) — NOT an individual bottle.

    Stores denormalized strings (product_name, capacity) because invoices
    are legal documents that must not change if inventory data changes.
    """
    


class Payment(models.Model):
    """
    Records a single payment event against an invoice.

    An invoice can receive multiple payments over time (e.g. partial cash
    payment on delivery, check for the balance later).
    Payment status on the invoice is computed from the sum of all payments —
    never stored directly, so it never goes out of sync.
    """
    