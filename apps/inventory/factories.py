import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from .models import InventoryItem, InventoryReservation
from apps.products.factories import ProductFactory
from apps.cart.factories import CartFactory
from django.utils import timezone
from datetime import timedelta
import random

class InventoryItemFactory(DjangoModelFactory):
    class Meta:
        model = InventoryItem
    
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=10, max=500)
    location = Faker('city')


class InventoryReservationFactory(DjangoModelFactory):
    class Meta:
        model = InventoryReservation
    
    cart = SubFactory(CartFactory)
    # order can be null
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=1, max=5)
    expires_at = factory.LazyAttribute(lambda obj: timezone.now() + timedelta(minutes=15))
