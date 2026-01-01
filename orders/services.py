import uuid
from django.db import transaction
from django.core.exceptions import ValidationError

from orders.models import Order, OrderItem, OrderStatus
from cart.models import Cart
from accounts.models import Address
from inventory.services import deduct_stock, restore_stock
from inventory.models import InventoryReservation
from payments.models import Payment


def _generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@transaction.atomic
def create_order_from_cart(user, address_id=None):
    """
    Orchestrates the checkout process:
    1. Validates Cart
    2. Validates/Selects Address
    3. Creates Order & OrderItems
    4. Deducts Physical Stock (Inventory)
    5. Clears Cart & Reservations
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

    # Process Items & Deduct Stock
    order_items = []

    for item in cart_items:
        # DEDUCT STOCK (The Service Call)
        # This will raise ValueError if stock is insufficient
        # Since we are in @transaction.atomic, the whole order rolls back if this fails
        try:
            deduct_stock(product=item.product, quantity=item.quantity)
        except ValueError as e:
            raise ValidationError(str(e))

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
    # Explicitly delete reservations first (safer than relying on signals)
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
        raise ValidationError("Cannot cancel a completed order. Please request a return.")

    if user_initiated and order.status not in [OrderStatus.PENDING_PAYMENT, OrderStatus.PAYMENT_FAILED]:
         raise ValidationError("Order is already processing. Contact support to cancel.")

    # Restore Stock
    # Iterate over items and add quantity back to inventory
    for item in order.items.all():
        try:
            restore_stock(product=item.product, quantity=item.quantity)
        except Exception as e:
            pass

    # Update Order Status
    order.status = OrderStatus.CANCELLED
    order.save()

    # Cancel Pending Payments
    Payment.objects.filter(
        order=order, 
        status=Payment.PaymentStatus.PENDING
    ).update(status=Payment.PaymentStatus.CANCELLED)

    return order