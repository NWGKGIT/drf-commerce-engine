import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatus
from apps.orders.services import cancel_order

from .models import InventoryReservation

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
    and releases held reservations.
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
            cancel_order(order, user_initiated=False)
            count += 1
            
    if count > 0:
        logger.info(f"Cancelled {count} unpaid orders and restored stock.")
    
    return f"Cancelled {count} orders"
