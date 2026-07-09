from django.db import models

from apps.cart.models import Cart
from apps.orders.models import Order
from apps.products.models import Product


class InventoryItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="inventory_items"
    )
    quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255, blank=True, null=True)  # optional
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} left"


class InventoryReservation(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reservations",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reservations",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    quantity = models.IntegerField()
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Inventory Reservations"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(cart__isnull=False, order__isnull=True)
                    | models.Q(cart__isnull=True, order__isnull=False)
                ),
                name="only_one_origin_source",
            ),
            models.UniqueConstraint(
                fields=["cart", "product"],
                condition=models.Q(cart__isnull=False),
                name="unique_cart_product_reservation",
            ),
            models.UniqueConstraint(
                fields=["order", "product"],
                condition=models.Q(order__isnull=False),
                name="unique_order_product_reservation",
            ),
        ]
        indexes = [
            models.Index(fields=['product', 'expires_at']),
        ]
