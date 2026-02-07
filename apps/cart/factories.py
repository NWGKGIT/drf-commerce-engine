import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from .models import Cart, CartItem
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory
from django.utils import timezone

class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart
        django_get_or_create = ('user',)

    user = SubFactory(UserFactory)
    # created_at = Faker('date_time_this_year')
    # updated_at = factory.LazyAttribute(lambda obj: obj.created_at)


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem
    
    cart = SubFactory(CartFactory)
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=1, max=3)
    # added_at = Faker('date_time_this_year')
