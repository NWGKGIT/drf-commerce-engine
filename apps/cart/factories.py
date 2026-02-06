import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from .models import Cart, CartItem
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart
    
    user = SubFactory(UserFactory)


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem
    
    cart = SubFactory(CartFactory)
    product = SubFactory(ProductFactory)
    quantity = Faker('random_int', min=1, max=5)
