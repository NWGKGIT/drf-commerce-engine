from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.products.factories import ProductFactory, CategoryFactory, ProductImageFactory
from apps.accounts.factories import UserFactory, UserProfileFactory, AddressFactory
from apps.orders.factories import OrderFactory, OrderItemFactory
from apps.reviews.factories import ReviewFactory
from apps.wishlist.factories import WishlistFactory, WishlistItemFactory
from apps.cart.factories import CartFactory, CartItemFactory
from apps.payments.factories import PaymentFactory
from apps.inventory.factories import InventoryItemFactory
from apps.products.models import Category, Product
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.wishlist.models import Wishlist
from apps.cart.models import Cart
from apps.payments.models import Payment
from apps.inventory.models import InventoryItem
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with realistic data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            # Order matters for deletion to avoid protected foreign keys
            Payment.objects.all().delete()
            OrderItemFactory._meta.model.objects.all().delete()
            Order.objects.all().delete()
            CartItemFactory._meta.model.objects.all().delete()
            Cart.objects.all().delete()
            WishlistItemFactory._meta.model.objects.all().delete()
            Wishlist.objects.all().delete()
            Review.objects.all().delete()
            InventoryItem.objects.all().delete()
            ProductImageFactory._meta.model.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            UserProfileFactory._meta.model.objects.all().delete()
            AddressFactory._meta.model.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data flushed successfully.'))

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        with transaction.atomic():
            # 1. Create Superuser (if not exists)
            if not User.objects.filter(email='admin@example.com').exists():
                User.objects.create_superuser('admin@example.com', 'adminpass123', first_name='System', last_name='Admin')
                self.stdout.write(self.style.SUCCESS('Superuser created (admin@example.com / adminpass123)'))

            # 2. Create Users
            self.stdout.write('Creating users...')
            users = UserFactory.create_batch(20)
            for user in users:
                UserProfileFactory(user=user)
                AddressFactory.create_batch(random.randint(1, 2), user=user)
            
            # 3. Create Categories and Products
            self.stdout.write('Creating products...')
            # We used an Iterator in ProductFactory, so we want to exhaust it or loop through it.
            # There are 19 products defined in the factory list.
            # Let's create all of them.
            products = []
            # We can create more than 19, the iterator will cycle. 
            # But let's stick to unique ones if possible, or just create 20 to be safe.
            for _ in range(20):
                product = ProductFactory()
                products.append(product)
                ProductImageFactory.create_batch(random.randint(1, 3), product=product)
                InventoryItemFactory(product=product)

            # 4. Create Orders
            self.stdout.write('Creating orders...')
            for user in users:
                # 50% chance a user has orders
                if random.choice([True, False]):
                    orders = OrderFactory.create_batch(random.randint(1, 3), user=user)
                    for order in orders:
                        # OrderFactory already creates items via post_generation, 
                        # but we can ensure payments are created
                        if order.total_amount > 0:
                            PaymentFactory(order=order)

            # 5. Create Reviews
            self.stdout.write('Creating reviews...')
            for product in products:
                # Random users review products
                reviewers = random.sample(users, k=random.randint(0, 5))
                for reviewer in reviewers:
                    ReviewFactory(user=reviewer, product=product)

            # 6. Create Wishlists and Carts
            self.stdout.write('Creating wishlists and carts...')
            for user in users:
                # Wishlist
                if random.choice([True, False]):
                    wishlist = WishlistFactory(user=user)
                    # Add random products
                    random_products = random.sample(products, k=random.randint(1, 5))
                    for p in random_products:
                        WishlistItemFactory(wishlist=wishlist, product=p)
                
                # Cart
                if random.choice([True, False]):
                    cart = CartFactory(user=user)
                    random_products = random.sample(products, k=random.randint(1, 3))
                    for p in random_products:
                        CartItemFactory(cart=cart, product=p)

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
