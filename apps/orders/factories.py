import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, Sequence
from .models import Order, OrderItem, OrderStatus
from apps.accounts.factories import UserFactory
from apps.products.factories import ProductFactory
from faker import Faker as FakerInstance

fake = FakerInstance()


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order
    
    user = SubFactory(UserFactory)
    order_number = Sequence(lambda n: f'ORD-{n:08d}')
    status = OrderStatus.PENDING_PAYMENT
    total_amount = Faker('pydecimal', left_digits=5, right_digits=2, positive=True, min_value=50, max_value=50000)
    currency = 'ETB'
    shipping_address_snapshot = factory.LazyFunction(lambda: {
        'address_line_1': fake.street_address(),
        'city': fake.city(),
        'region': fake.state(),
        'postal_code': fake.postcode(),
        'country': fake.country()
    })


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem
    
    order = SubFactory(OrderFactory)
    product = SubFactory(ProductFactory)
    product_name = LazyAttribute(lambda obj: obj.product.name)
    quantity = Faker('random_int', min=1, max=5)
    unit_price = LazyAttribute(lambda obj: obj.product.final_price)
    total_price = LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
