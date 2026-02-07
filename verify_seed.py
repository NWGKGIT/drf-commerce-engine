import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.products.models import Product
from apps.orders.models import Order
from apps.accounts.models import User

print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"Users: {User.objects.count()}")
