import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from .models import Review
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory
import random

class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    user = SubFactory(UserFactory)
    product = SubFactory(ProductFactory)
    rating = Faker('random_int', min=3, max=5) # Skew towards positive reviews
    
    # Use real-world-like reviews
    comment = Faker('paragraph', nb_sentences=random.randint(1, 3))
    
    is_verified_purchase = Faker('boolean', chance_of_getting_true=80)
    # created_at = Faker('date_time_this_year')
    # updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
