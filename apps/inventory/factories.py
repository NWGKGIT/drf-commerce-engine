import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute
from .models import InventoryItem, InventoryReservation
from apps.products.factories import ProductFactory
from apps.cart.factories import CartFactory
from django.utils import timezone
from datetime import timedelta


class InventoryItemFactory(DjangoModelFactory):
    class Meta:
        model = InventoryItem
    
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=50, max=500)
    location = Faker('city')


class InventoryReservationFactory(DjangoModelFactory):
    class Meta:
        model = InventoryReservation
    
    cart = SubFactory(CartFactory)
    order = None  # Will be set when creating order-related reservations
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=1, max=10)
    expires_at = LazyAttribute(lambda obj: timezone.now() + timedelta(minutes=15))
