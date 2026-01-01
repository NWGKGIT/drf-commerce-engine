from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from .models import InventoryReservation, InventoryItem
from orders.models import Order, OrderStatus

logger = logging.getLogger(__name__)

@shared_task
def clear_expired_reservations():
    """
    Deletes InventoryReservation records that have passed their expiration time.
    (Handles items currently in carts but not ordered)
    """
    now = timezone.now()
    expired_reservations = InventoryReservation.objects.filter(expires_at__lte=now)

    count = expired_reservations.count()

    if count > 0:
        expired_reservations.delete()
        logger.info(f"Released {count} expired inventory reservations.")
    
    return f"Cleared {count} reservations"


@shared_task
def cancel_unpaid_orders():
    """
    Cancels orders that have been 'Pending Payment' for too long 
    and returns the stock to inventory.
    (Handles items where Order was created -> Stock Deducted -> User abandoned payment)
    """
    # Define timeout 
    timeout_threshold = timezone.now() - timedelta(minutes=30)
    
    # Find stale orders
    stale_orders = Order.objects.filter(
        status=OrderStatus.PENDING_PAYMENT,
        created_at__lte=timeout_threshold
    )
    
    count = 0
    for order in stale_orders:
        with transaction.atomic():
            # Refill Inventory
            for order_item in order.items.all():
                # Add back to the first available inventory pile for this product
                # In a complex warehouse, you might have a specific 'Returns' location
                inventory_item = InventoryItem.objects.filter(
                    product=order_item.product
                ).first()
                
                if inventory_item:
                    inventory_item.quantity += order_item.quantity
                    inventory_item.save()
                else:
                    # If no inventory row exists (rare), create one or log warning
                    InventoryItem.objects.create(
                        product=order_item.product,
                        quantity=order_item.quantity,
                        location="Restocked from Cancelled Order"
                    )

            # Mark Order Cancelled
            order.status = OrderStatus.CANCELLED
            order.save()
            count += 1
            
    if count > 0:
        logger.info(f"Cancelled {count} unpaid orders and restored stock.")
    
    return f"Cancelled {count} orders"