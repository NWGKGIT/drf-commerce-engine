import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from .models import Review
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review
    
    user = SubFactory(UserFactory)
    product = SubFactory(ProductFactory)
    rating = Faker('random_int', min=1, max=5)
    comment = Faker('paragraph', nb_sentences=3)
    is_verified_purchase = Faker('boolean', chance_of_getting_true=70)
