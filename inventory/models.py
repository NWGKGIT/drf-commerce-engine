from django.db import models
from products.models import Product
from cart.models import Cart
from orders.models import Order

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Inventory Reservations"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(cart__isnull=False, order__isnull=True)
                    | models.Q(cart__isnull=True, order__isnull=False)
                ),
                name="only_one_origin_source",
            )
        ]
        unique_together = ("cart", "product")