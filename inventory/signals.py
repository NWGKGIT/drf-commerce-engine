from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from cart.models import CartItem
from .models import InventoryReservation, InventoryItem
from products.models import Product
from django.db import transaction
from django.db.models import Sum

@receiver(post_save, sender=CartItem)
def reserve_stock_on_add_to_cart(sender, instance, created, **kwargs):
    with transaction.atomic():
        # Remove expired reservations for this product first
        InventoryReservation.objects.filter(
            product=instance.product,
            expires_at__lte=timezone.now()
        ).delete()

        physical_stock = InventoryItem.objects.filter(
            product=instance.product
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # Calculate Active Reservations (excluding this cart)
        active_reservations = InventoryReservation.objects.filter(
            product=instance.product, 
            expires_at__gt=timezone.now()
        ).exclude(cart=instance.cart).aggregate(total=Sum('quantity'))['total'] or 0

        available = physical_stock - active_reservations

        # Validation Logic
        if instance.quantity > available:
            reservation_qty = available
        else:
            reservation_qty = instance.quantity

        if reservation_qty > 0:
            InventoryReservation.objects.update_or_create(
                cart=instance.cart,
                product=instance.product,
                defaults={
                    'quantity': reservation_qty,
                    'expires_at': timezone.now() + timedelta(minutes=15)
                }
            )
        else:
            # If 0 available, ensure we don't hold a reservation record with 0 qty
            InventoryReservation.objects.filter(cart=instance.cart, product=instance.product).delete()