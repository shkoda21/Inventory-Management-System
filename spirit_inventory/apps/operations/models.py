from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime

from apps.inventory.models import Product, Retailer


class SellOrder(models.Model):
    """
    Internal sell order — tracks individual bottles sold to a retailer.
    This is the source of truth for inventory movement and TTB reporting.
    NOT the same as an Invoice (which is an aggregated customer document).
    """
    name = models.CharField(max_length=500, blank=True)
    retailer = models.ForeignKey(
        Retailer,
        on_delete=models.PROTECT,
        related_name='sell_orders',
    )
    sell_date = models.DateField()
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    extra_notice = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-sell_date', '-pk']
        indexes = [
            models.Index(fields=['-sell_date']),
            models.Index(fields=['retailer']),
        ]

    def __str__(self):
        return self.name or f"Sell Order #{self.pk}"

    def get_absolute_url(self):
        return reverse('operations:sell_order_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.name:
            # Generate name after first save when pk is available
            is_new = not self.pk
            super().save(*args, **kwargs)
            if is_new:
                self.name = (
                    f"Sell #{self.pk} — "
                    f"{self.retailer} — "
                    f"{self.sell_date} — "
                    f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                SellOrder.objects.filter(pk=self.pk).update(name=self.name)
            return
        super().save(*args, **kwargs)

    def update_total(self):
        total = self.items.aggregate(s=Sum('price'))['s'] or Decimal('0.00')
        self.total_price = total
        SellOrder.objects.filter(pk=self.pk).update(total_price=total)

    def add_item(self, product):
        """
        Add a single bottle to this order. Validates stock, date, and
        return history before committing.
        """
        return item

    def remove_item(self, product):
        try:
            item = SellItem.objects.get(order=self, product=product)
            item.delete()
            product.in_stock = True
            product.save(update_fields=['in_stock'])
            self.update_total()
        except SellItem.DoesNotExist:
            raise ValueError(f"Bottle #{product.bottle_number} is not in this order.")

    def calculate_total_return_amount(self):
        return sum(
            r.total_return_price for r in self.return_orders.all()
        )

    def calculate_net_profit(self):
        return self.total_price - self.calculate_total_return_amount()


class SellItem(models.Model):
    """One row = one physical bottle in a sell order."""
    order = models.ForeignKey(
        SellOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sell_items',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product} — ${self.price}"


class ReturnOrder(models.Model):
    """
    Return of bottles previously sold in a SellOrder.
    Products are restored to in_stock=True on creation.
    """
    name = models.CharField(max_length=500, blank=True)
    sell_order = models.ForeignKey(
        SellOrder,
        on_delete=models.PROTECT,
        related_name='return_orders',
    )
    date_return = models.DateField()
    total_return_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    extra_notice = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date_return', '-pk']

    def __str__(self):
        return self.name or f"Return #{self.pk}"

    def get_absolute_url(self):
        return reverse('operations:return_order_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.name:
            is_new = not self.pk
            super().save(*args, **kwargs)
            if is_new:
                self.name = (
                    f"Return #{self.pk} — "
                    f"for Sell #{self.sell_order.pk} — "
                    f"{self.date_return}"
                )
                ReturnOrder.objects.filter(pk=self.pk).update(name=self.name)
            return
        super().save(*args, **kwargs)

    def update_total(self):
        total = self.items.aggregate(s=Sum('price'))['s'] or Decimal('0.00')
        self.total_return_price = total
        ReturnOrder.objects.filter(pk=self.pk).update(total_return_price=total)

    def add_item(self, product):
        if not self.sell_order.items.filter(product=product).exists():
            raise ValueError(f"Bottle #{product.bottle_number} is not in the original sell order.")
        sell_item = self.sell_order.items.get(product=product)
        item, created = ReturnItem.objects.get_or_create(
            return_order=self,
            product=product,
            defaults={'price': sell_item.price},
        )
        if not created:
            raise ValueError(f"Bottle #{product.bottle_number} is already in this return.")
        product.in_stock = True
        product.save(update_fields=['in_stock'])
        self.update_total()
        return item

    def remove_item(self, product):
        try:
            item = ReturnItem.objects.get(return_order=self, product=product)
            item.delete()
            product.in_stock = False
            product.save(update_fields=['in_stock'])
            self.update_total()
        except ReturnItem.DoesNotExist:
            raise ValueError(f"Bottle #{product.bottle_number} is not in this return.")


class ReturnItem(models.Model):
    """One row = one returned physical bottle."""
    return_order = models.ForeignKey(
        ReturnOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='return_items',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('return_order', 'product')

    def __str__(self):
        return f"{self.product} — ${self.price}"


class WriteOff(models.Model):
    """
    A bottle permanently removed from inventory due to breakage,
    spoilage, quality failure, or other reasons.
    Enforced one-per-product at the DB level.
    """
    REASON_CHOICES = [
        ('breakage',    'Breakage'),
        ('spoilage',    'Spoilage / Quality failure'),
        ('label',       'Label defect'),
        ('compliance',  'Compliance / Regulatory'),
        ('sampling',    'Sampling / Testing'),
        ('other',       'Other'),
    ]

    # your model fields and methods here