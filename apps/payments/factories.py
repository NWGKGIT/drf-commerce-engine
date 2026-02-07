import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute
from .models import Payment
from apps.orders.factories import OrderFactory
import uuid

class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment
    
    order = SubFactory(OrderFactory)
    amount = LazyAttribute(lambda obj: obj.order.total_amount)
    currency = 'ETB'
    status = Faker('random_element', elements=[s[0] for s in Payment.PaymentStatus.choices])
    provider = Faker('random_element', elements=['chapa', 'stripe', 'paypal'])
    
    # reference is auto-generated in model.save() if not provided.
    # We can rely on that or provide one.
    # reference = LazyAttribute(lambda obj: str(uuid.uuid4()))
    
    raw_response = factory.LazyFunction(lambda: {
        'message': 'Payment processed successfully',
        'status': 'success',
        'meta': {'trace_id': str(uuid.uuid4())}
    })
    # created_at and updated_at are auto, so we don't set them here.
