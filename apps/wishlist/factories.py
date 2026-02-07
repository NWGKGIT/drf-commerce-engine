import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from .models import Wishlist, WishlistItem
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory

class WishlistFactory(DjangoModelFactory):
    class Meta:
        model = Wishlist
        django_get_or_create = ('user',) # Usually one per user?

    user = SubFactory(UserFactory)


class WishlistItemFactory(DjangoModelFactory):
    class Meta:
        model = WishlistItem
    
    wishlist = SubFactory(WishlistFactory)
    product = SubFactory(ProductFactory)
    # added_at = Faker('date_time_this_year')
