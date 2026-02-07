import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, post_generation
from django.contrib.auth import get_user_model
from .models import UserProfile, Address
import random
from faker import Faker as FakerInstance

User = get_user_model()
fake = FakerInstance()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    is_staff = False

    @post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('testpass123')


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = SubFactory(UserFactory)
    birth_date = Faker('date_of_birth', minimum_age=18, maximum_age=70)
    profile_picture = Faker('image_url', width=400, height=400)
    
    @factory.lazy_attribute
    def preferences(self):
        return {
            'newsletter': random.choice([True, False]),
            'notifications': random.choice([True, False]),
            'theme': random.choice(['light', 'dark', 'system']),
            'currency': 'ETB',
            'language': 'en'
        }


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    user = SubFactory(UserFactory)
    address_line_1 = Faker('street_address')
    address_line_2 = Faker('secondary_address')
    city = Faker('city')
    region = Faker('state')
    postal_code = Faker('postcode')
    country = Faker('country_code')
    
    @factory.lazy_attribute
    def location_pin(self):
        return {
            'lat': float(fake.latitude()),
            'lng': float(fake.longitude())
        }
    
    is_default = False
