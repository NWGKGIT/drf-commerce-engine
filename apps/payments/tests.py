from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
import requests
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import Address
from apps.cart.models import Cart, CartItem
from apps.inventory.models import InventoryItem, InventoryReservation
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.orders.services import cancel_order, create_order_from_cart
from apps.payments.models import Payment
from apps.payments.services import ChapaService, finalize_order
from apps.products.models import Category, Product


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Laptops", slug="laptops")
    return Product.objects.create(
        category=category,
        name="Work Laptop",
        slug="work-laptop",
        sku="SKU-001",
        price=Decimal("100.00"),
    )


@pytest.fixture
def user_with_address(django_user_model):
    user = django_user_model.objects.create_user(
        email="buyer@example.com",
        password="StrongPass123!",
    )
    Address.objects.create(
        user=user,
        address_line_1="Main Street",
        city="Addis Ababa",
        region="Addis Ababa",
        country="ET",
        is_default=True,
    )
    return user


def _pending_order(user, product, total=Decimal("100.00")):
    order = Order.objects.create(
        user=user,
        order_number="ORD-TEST-001",
        status=OrderStatus.PENDING_PAYMENT,
        total_amount=total,
        shipping_address_snapshot={"address_line_1": "Main Street"},
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        quantity=1,
        unit_price=product.price,
        total_price=product.price,
    )
    return order


@pytest.mark.django_db
def test_create_order_moves_cart_reservation_without_deducting_stock(user_with_address, product):
    InventoryItem.objects.create(product=product, quantity=5)
    cart, _ = Cart.objects.get_or_create(user=user_with_address)
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    order = create_order_from_cart(user_with_address)

    assert order.status == OrderStatus.PENDING_PAYMENT
    assert InventoryItem.objects.filter(product=product).aggregate(total=Sum("quantity"))[
        "total"
    ] == 5
    assert not InventoryReservation.objects.filter(cart=cart).exists()
    assert InventoryReservation.objects.get(order=order, product=product).quantity == 2
    assert not cart.items.exists()


@pytest.mark.django_db
def test_finalize_order_deducts_stock_once_and_clears_order_reservation(user_with_address, product):
    inventory = InventoryItem.objects.create(product=product, quantity=5)
    order = _pending_order(user_with_address, product)
    InventoryReservation.objects.create(
        order=order,
        product=product,
        quantity=1,
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    payment = Payment.objects.create(order=order, amount=order.total_amount)

    assert finalize_order(payment.reference, gateway_response={"status": "success"}) is True

    payment.refresh_from_db()
    order.refresh_from_db()
    inventory.refresh_from_db()

    assert payment.status == Payment.PaymentStatus.SUCCESS
    assert order.status == OrderStatus.PROCESSING
    assert order.stock_deducted is True
    assert inventory.quantity == 4
    assert not InventoryReservation.objects.filter(order=order).exists()

    assert finalize_order(payment.reference, gateway_response={"status": "success"}) is True
    inventory.refresh_from_db()
    assert inventory.quantity == 4


@pytest.mark.django_db
def test_finalize_cancelled_payment_does_not_mark_success(user_with_address, product):
    order = _pending_order(user_with_address, product)
    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        status=Payment.PaymentStatus.CANCELLED,
    )

    assert finalize_order(payment.reference, gateway_response={"status": "success"}) is False

    payment.refresh_from_db()
    order.refresh_from_db()
    assert payment.status == Payment.PaymentStatus.CANCELLED
    assert order.status == OrderStatus.PENDING_PAYMENT


@pytest.mark.django_db
def test_cancel_pending_order_releases_reservation_without_restoring_stock(
    user_with_address,
    product,
):
    InventoryItem.objects.create(product=product, quantity=5)
    order = _pending_order(user_with_address, product)
    InventoryReservation.objects.create(
        order=order,
        product=product,
        quantity=1,
        expires_at=timezone.now() + timedelta(minutes=30),
    )

    cancel_order(order, user_initiated=True)

    order.refresh_from_db()
    assert order.status == OrderStatus.CANCELLED
    assert order.stock_deducted is False
    assert InventoryItem.objects.filter(product=product).aggregate(total=Sum("quantity"))[
        "total"
    ] == 5
    assert not InventoryReservation.objects.filter(order=order).exists()


@pytest.mark.django_db
def test_cancel_stock_deducted_order_restores_stock(user_with_address, product):
    InventoryItem.objects.create(product=product, quantity=4)
    order = _pending_order(user_with_address, product)
    order.status = OrderStatus.PAYMENT_FAILED
    order.stock_deducted = True
    order.save(update_fields=["status", "stock_deducted"])

    cancel_order(order, user_initiated=True)

    order.refresh_from_db()
    assert order.status == OrderStatus.CANCELLED
    assert order.stock_deducted is False
    assert InventoryItem.objects.filter(product=product).aggregate(total=Sum("quantity"))[
        "total"
    ] == 5


def test_initiate_payment_requires_chapa_configuration(settings):
    settings.CHAPA_SECRET_KEY = None
    settings.BACKEND_URL = "https://api.example.test"
    payment = SimpleNamespace(
        order=SimpleNamespace(
            user=SimpleNamespace(
                email="buyer@example.com",
                first_name="",
                last_name="",
            ),
            order_number="ORD-1",
        ),
        amount=Decimal("100.00"),
        currency="ETB",
        reference="TX-1",
    )

    with pytest.raises(ValueError, match="Chapa secret key is not configured"):
        ChapaService.initiate_payment(payment, "https://frontend.example.test/return")


def test_initiate_payment_uses_timeout_and_handles_provider_error(settings, mocker):
    settings.CHAPA_SECRET_KEY = "secret"
    settings.BACKEND_URL = "https://backend.example.test"
    settings.CHAPA_REQUEST_TIMEOUT = 3
    payment = mocker.Mock()
    payment.amount = Decimal("100.00")
    payment.currency = "ETB"
    payment.reference = "TX-1"
    payment.order.user.email = "buyer@example.com"
    payment.order.user.first_name = ""
    payment.order.user.last_name = ""
    payment.order.order_number = "ORD-1"
    response = mocker.Mock()
    response.raise_for_status.side_effect = requests.HTTPError("bad gateway")
    mock_post = mocker.patch("apps.payments.services.requests.post", return_value=response)

    with pytest.raises(ValueError, match="Connection Error"):
        ChapaService.initiate_payment(payment, "https://frontend.example.test/return")

    assert mock_post.call_args.kwargs["timeout"] == 3
