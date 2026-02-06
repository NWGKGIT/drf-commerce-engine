import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute
from django.contrib.auth import get_user_model
from .models import UserProfile, Address
import random

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    is_staff = False
    
    @factory.post_generation
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
    birth_date = Faker('date_of_birth', minimum_age=18, maximum_age=80)
    profile_picture = Faker('image_url')
    preferences = factory.LazyFunction(lambda: {
        'newsletter': True,
        'notifications': True,
        'theme': 'light'
    })


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address
    
    user = SubFactory(UserFactory)
    address_line_1 = Faker('street_address')
    address_line_2 = Faker('secondary_address')
    city = Faker('city')
    region = Faker('state')
    postal_code = Faker('postcode')
    country = Faker('country')
    location_pin = factory.LazyFunction(lambda: {
        'lat': round(random.uniform(-90, 90), 6),
        'lng': round(random.uniform(-180, 180), 6)
    })
    is_default = False
