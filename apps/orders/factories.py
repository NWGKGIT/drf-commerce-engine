import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, Sequence, post_generation
from .models import Order, OrderItem, OrderStatus
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory
from django.utils import timezone
import random
from decimal import Decimal
from faker import Faker as FakerInstance

fake = FakerInstance()

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order
    
    user = SubFactory(UserFactory)
    order_number = Sequence(lambda n: f'ORD-{timezone.now().year}-{n:06d}')
    status = Faker('random_element', elements=[s[0] for s in OrderStatus.choices])
    
    total_amount = Decimal('0.00')
    currency = 'ETB'
    
    shipping_address_snapshot = factory.LazyAttribute(lambda obj: {
        'address_line_1': fake.street_address(),
        'city': fake.city(),
        'region': fake.state(),
        'postal_code': fake.postcode(),
        'country': fake.country_code()
    })

    created_at = Faker('date_time_this_year', tzinfo=timezone.get_current_timezone())
    # updated_at is auto_now, so we can't set it directly in create()
    # updated_at = LazyAttribute(lambda obj: obj.created_at)

    @post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for item in extracted:
                self.items.add(item)
        else:
            OrderItemFactory.create_batch(random.randint(1, 5), order=self)
            
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.save()


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem
    
    order = SubFactory(OrderFactory)
    product = SubFactory(ProductFactory)
    product_name = LazyAttribute(lambda obj: obj.product.name)
    quantity = Faker('random_int', min=1, max=3)
    
    unit_price = LazyAttribute(lambda obj: obj.product.price)
    
    total_price = LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
