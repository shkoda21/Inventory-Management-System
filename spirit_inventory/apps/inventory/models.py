"""
Public portfolio version of inventory models.

NOTE:
This module is intentionally simplified."""


from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class Capacity(models.Model):
    """
    Bottle size. Stores the TTB wine gallon constant so the report
    calculation is fully data-driven — no hardcoded values in Python.
    """
    WINE_GALLON_CONSTANTS = {
        'capacity':  value,
    }

    name = models.CharField(max_length=50, unique=True)
    wine_gallons_per_bottle = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        null=True,
        blank=True,
        help_text='TTB wine gallon constant for this bottle size.',
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Display order in dropdowns (smallest to largest).',
    )
    extra_notice = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Capacities'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-populate wine gallon constant from known values if not set
        
        super().save(*args, **kwargs)


class TypeLiqueur(models.Model):
    """
    Product type / spirit category. e.g. Vodka, Honey liqueur, Cherry liqueur.
    Alcohol volume is NOT stored here — it lives on Batch because the same
    type can be produced at different proofs across batches.
    """
    name = models.CharField(max_length=100, unique=True)
    extra_notice = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Liqueur Type'
        verbose_name_plural = 'Liqueur Types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Barcode(models.Model):
    """
    Barcode assigned to a product type + capacity combination.
    One barcode can apply to many individual bottles.
    """



class Batch(models.Model):
    """
    A production run. Each batch has a specific alcohol volume (proof),
    which is critical for TTB calculations. The same TypeLiqueur can
    appear in multiple batches at different alcohol volumes.
    """
    name = models.CharField(max_length=100, unique=True)
    type = models.ForeignKey(
        TypeLiqueur,
        on_delete=models.PROTECT,
        related_name='batches',
    )
    alcohol_volume = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Alcohol by volume percentage, e.g. 40.00 for 40%.',
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    #Add additional fields as needed, e.g. production date, notes, etc.

    class Meta:
        verbose_name_plural = 'Batches'
        ordering = ['-start_date', 'name']

    def __str__(self):
        return f"{self.name} ({self.type} {self.alcohol_volume}%)"

    def get_absolute_url(self):
        return reverse('inventory:batch_detail', args=[self.pk])

    #@property methods for display formatting, production status, etc. can be added here.


class Ingredient(models.Model):
    """Ingredient used in a specific batch."""

    UNIT_CHOICES = [
        ...
    ]

    batch = models.ForeignKey(
        Batch,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=300)
    # Additional fields for quantity, unit of measure, supplier, etc. can be added as needed.

class Product(models.Model):
    """
    Represents a single physical bottle. Every product instance is unique,
    identified by the combination of batch + capacity + bottle_number.

    This is the atom of the inventory system. Each bottle has its own
    lifecycle: produced → sold → returned / written off.
    """
         # ... Add your fields as needed.

    class Meta:
        unique_together = ('batch', 'capacity', 'bottle_number')
        ordering = ['batch', 'capacity', 'bottle_number']
        indexes = [
            models.Index(fields=['in_stock']),
            models.Index(fields=['batch', 'capacity']),
        ]

    def __str__(self):
        return (
            f"{self.batch.type} {self.capacity} "
            f"— Batch: {self.batch.name} "
            f"— Bottle #{self.bottle_number}"
        )

    def get_absolute_url(self):
        return reverse('inventory:product_detail', args=[self.pk])

    #@property methods for display formatting, stock status, etc. can be added here.
    

class Retailer(models.Model):
    """
    The single source of truth for customer data.
    Represents a unique selling point: one legal entity (organization)
    at one physical location (store).

    One organization can appear multiple times with different store details
    — each store has its own unique license.

    Invoice uses: organization_name, license, organization_address
    Sell order stores: all fields for operational tracking
    """
    # --- Legal entity fields — always appear on invoice ---
    organization_name    = models.CharField(max_length=255, db_index=True)
    license              = models.CharField(
        max_length=100,
        unique=True,
        help_text='Each store has a unique license.',
    )
    organization_address = models.TextField()
    organization_email   = models.EmailField(null=True, blank=True)
    organization_phone   = models.CharField(max_length=20, null=True, blank=True)
    contact_person       = models.CharField(max_length=100, null=True, blank=True)

    # --- Store-level fields — operational use only, never on invoice ---
    store_name    = models.CharField(
        max_length=255,
        blank=True,
        help_text='Leave blank if store name = organization name.',
    )
    store_address = models.TextField(blank=True)
    extra_notice = models.CharField(max_length=2000, null=True, blank=True)
    
    class Meta:
        # A store name is unique within an organization (by license)
        unique_together = ('license', 'store_name')
        ordering = ['organization_name', 'store_name']

    def __str__(self):
        if self.store_name and self.store_name != self.organization_name:
            return f"{self.store_name} ({self.organization_name})"
        return self.organization_name

    def get_absolute_url(self):
        return reverse('inventory:retailer_detail', args=[self.pk])

    #@property methods for display formatting, store information, etc. can be added here.

        