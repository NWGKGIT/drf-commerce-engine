from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Sum

class Category(models.Model):
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
        db_index=True,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['parent_category', 'is_active']),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )  
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default="ETB")
    specifications = models.JSONField(default=dict)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount_price is not None and self.discount_price < self.price:
            return self.discount_price
        return self.price

    def clean(self):
        super().clean()
        if self.price < 0:
            raise ValidationError("Price Can't be negative.")
        if self.discount_price is not None and self.discount_price < 0:
            raise ValidationError("Discount price cannot be negative.")
        if self.discount_price is not None and self.discount_price > self.price:
            raise ValidationError(
                "Discount price cannot be greater than the original price."
            )




class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "is_main"]
