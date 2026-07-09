import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Address
from apps.cart.models import Cart
from apps.inventory.models import InventoryReservation
from apps.inventory.services import restore_stock
from apps.orders.models import Order, OrderItem, OrderStatus

# from apps.payments.models import Payment
from .signals import order_cancelled_signal


def _generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@transaction.atomic
def create_order_from_cart(user, address_id=None):
    """
    Orchestrates the checkout process:
    1. Validates Cart
    2. Validates/Selects Address
    3. Creates Order & OrderItems
    4. Moves active Cart reservations to the pending Order
    5. Clears Cart items
    """

    cart = Cart.objects.filter(user=user).prefetch_related("items__product").first()
    if not cart or not cart.items.exists():
        raise ValidationError("Cart is empty.")

    if address_id:
        address = Address.objects.filter(id=address_id, user=user).first()
        if not address:
            raise ValidationError("Invalid shipping address ID.")
    else:
        address = Address.objects.filter(user=user, is_default=True).first()

    if not address:
        raise ValidationError("No shipping address provided and no default found.")

    # Create Order
    cart_items = cart.items.all()
    total_amount = sum(item.quantity * item.product.price for item in cart_items)

    address_snapshot = {
        "address_line_1": address.address_line_1,
        "city": address.city,
        "country": address.country,
        # Add other fields as necessary
    }

    order = Order.objects.create(
        user=user,
        order_number=_generate_order_number(),
        total_amount=total_amount,
        shipping_address_snapshot=address_snapshot,
        status="pending_payment",  # Enum value
    )

    # Process Items. Physical stock is deducted after payment succeeds.
    order_items = []

    for item in cart_items:
        active_reservation = InventoryReservation.objects.filter(
            cart=cart,
            product=item.product,
            quantity__gte=item.quantity,
            expires_at__gt=timezone.now(),
        ).first()

        if not active_reservation:
            raise ValidationError(
                f"Reserved stock for {item.product.name} has expired or is insufficient."
            )

        # Create Order Item
        order_items.append(
            OrderItem(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.product.price,
                total_price=item.quantity * item.product.price,
            )
        )

    OrderItem.objects.bulk_create(order_items)

    # Cleanup
    reservation_expires_at = timezone.now() + timedelta(minutes=30)
    for item in cart_items:
        InventoryReservation.objects.update_or_create(
            order=order,
            product=item.product,
            defaults={
                "cart": None,
                "quantity": item.quantity,
                "expires_at": reservation_expires_at,
            },
        )

    InventoryReservation.objects.filter(cart=cart).delete()

    # Delete cart items
    cart.items.all().delete()

    # Delete the cart itself if you want a fresh cart ID every time
    # cart.delete()

    return order


@transaction.atomic
def cancel_order(order, user_initiated=False):
    """
    Cancels an order, restores inventory, and voids pending payments.
    """
    if order.status == OrderStatus.CANCELLED:
        return order

    if order.status == OrderStatus.COMPLETED:
        raise ValidationError(
            "Cannot cancel a completed order. Please request a return."
        )

    if user_initiated and order.status not in [
        OrderStatus.PENDING_PAYMENT,
        OrderStatus.PAYMENT_FAILED,
    ]:
        raise ValidationError("Order is already processing. Contact support to cancel.")

    if order.stock_deducted:
        # Restore stock only if successful payment finalization already deducted it.
        for item in order.items.all():
            restore_stock(product=item.product, quantity=item.quantity)
        order.stock_deducted = False
    else:
        InventoryReservation.objects.filter(order=order).delete()

    # Update Order Status
    order.status = OrderStatus.CANCELLED
    order.save(update_fields=["status", "stock_deducted", "updated_at"])

    # Cancel any pending payments tied to this order so a user cannot
    # trigger a Chapa payment on an already-cancelled order via a stale link.
    from apps.payments.models import Payment
    Payment.objects.filter(
        order=order, status=Payment.PaymentStatus.PENDING
    ).update(status=Payment.PaymentStatus.CANCELLED)

    order_cancelled_signal.send(sender=order.__class__, order=order)
    return order
