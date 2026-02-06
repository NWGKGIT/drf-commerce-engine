from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from decimal import Decimal
import random

# Import all factories
from apps.accounts.factories import UserFactory, AddressFactory
from apps.products.factories import CategoryFactory, ProductFactory, ProductImageFactory
from apps.inventory.factories import InventoryItemFactory
from apps.cart.factories import CartFactory, CartItemFactory
from apps.orders.factories import OrderFactory, OrderItemFactory
from apps.payments.factories import PaymentFactory
from apps.reviews.factories import ReviewFactory
from apps.wishlist.factories import WishlistFactory, WishlistItemFactory

# Import models
from apps.products.models import Category, Product
from apps.inventory.models import InventoryItem
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.payments.models import Payment
from apps.wishlist.models import Wishlist

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with realistic sample data using factory-boy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)',
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Number of products to create (default: 50)',
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=20,
            help='Number of orders to create (default: 20)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('Data cleared successfully!'))

        num_users = options['users']
        num_products = options['products']
        num_orders = options['orders']

        self.stdout.write(self.style.MIGRATE_HEADING('Starting database seeding...'))

        try:
            with transaction.atomic():
                # Step 1: Create Users (UserProfile created automatically via signal)
                self.stdout.write('Creating users...')
                users = []
                for i in range(num_users):
                    user = UserFactory()
                    users.append(user)
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {num_users} users'))

                # Step 2: Create Addresses for users
                self.stdout.write('Creating addresses...')
                addresses_created = 0
                for user in users:
                    # Create 1-3 addresses per user
                    num_addresses = random.randint(1, 3)
                    for j in range(num_addresses):
                        AddressFactory(user=user, is_default=(j == 0))
                        addresses_created += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {addresses_created} addresses'))

                # Step 3: Create Categories (some with parent categories)
                self.stdout.write('Creating categories...')
                parent_categories = []
                for _ in range(5):
                    parent_cat = CategoryFactory()
                    parent_categories.append(parent_cat)
                
                # Create subcategories
                subcategories = []
                for parent in parent_categories:
                    for _ in range(random.randint(2, 4)):
                        subcat = CategoryFactory(parent_category=parent)
                        subcategories.append(subcat)
                
                all_categories = parent_categories + subcategories
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {len(all_categories)} categories'))

                # Step 4: Create Products
                self.stdout.write('Creating products...')
                products = []
                for _ in range(num_products):
                    category = random.choice(all_categories)
                    product = ProductFactory(category=category)
                    products.append(product)
                    
                    # Add 1-5 images per product
                    num_images = random.randint(1, 5)
                    for j in range(num_images):
                        ProductImageFactory(
                            product=product,
                            is_main=(j == 0),
                            position=j
                        )
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {num_products} products with images'))

                # Step 5: Create Inventory Items for all products
                self.stdout.write('Creating inventory items...')
                for product in products:
                    # Create 50-500 units of stock per product
                    InventoryItemFactory(product=product, quantity=random.randint(50, 500))
                self.stdout.write(self.style.SUCCESS(f'[OK] Created inventory items for {num_products} products'))

                # Step 6: Create Shopping Carts for some users
                self.stdout.write('Creating shopping carts...')
                carts_created = 0
                for user in random.sample(users, min(len(users), num_users // 2)):
                    cart = CartFactory(user=user)
                    # Add 1-5 items to cart
                    num_items = random.randint(1, 5)
                    for _ in range(num_items):
                        product = random.choice(products)
                        # Ensure we don't exceed available stock
                        try:
                            inventory = InventoryItem.objects.filter(product=product).first()
                            if inventory:
                                max_qty = min(5, inventory.quantity)
                                if max_qty > 0:
                                    CartItemFactory(
                                        cart=cart,
                                        product=product,
                                        quantity=random.randint(1, max_qty)
                                    )
                        except Exception:
                            pass
                    carts_created += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {carts_created} shopping carts'))

                # Step 7: Create Orders with OrderItems
                self.stdout.write('Creating orders...')
                orders = []
                for _ in range(num_orders):
                    user = random.choice(users)
                    
                    # Get one of the user's addresses for snapshot
                    user_addresses = user.addresses.all()
                    if user_addresses.exists():
                        address = user_addresses.first()
                        shipping_snapshot = {
                            'address_line_1': address.address_line_1,
                            'address_line_2': address.address_line_2 or '',
                            'city': address.city,
                            'region': address.region,
                            'postal_code': address.postal_code or '',
                            'country': address.country
                        }
                    else:
                        # Fallback if no address
                        shipping_snapshot = {
                            'address_line_1': '123 Main St',
                            'city': 'Addis Ababa',
                            'region': 'Addis Ababa',
                            'postal_code': '1000',
                            'country': 'Ethiopia'
                        }
                    
                    order = OrderFactory(
                        user=user,
                        shipping_address_snapshot=shipping_snapshot,
                        status=random.choice(list(OrderStatus.choices))[0]
                    )
                    
                    # Add 1-5 items to the order
                    num_items = random.randint(1, 5)
                    order_total = Decimal('0.00')
                    
                    for _ in range(num_items):
                        product = random.choice(products)
                        
                        # Ensure quantity doesn't exceed available stock
                        try:
                            inventory = InventoryItem.objects.filter(product=product).first()
                            if inventory:
                                max_qty = min(5, inventory.quantity)
                                
                                if max_qty > 0:
                                    quantity = random.randint(1, max_qty)
                                    unit_price = product.final_price
                                    total_price = unit_price * quantity
                                    
                                    OrderItemFactory(
                                        order=order,
                                        product=product,
                                        product_name=product.name,
                                        quantity=quantity,
                                        unit_price=unit_price,
                                        total_price=total_price
                                    )
                                    
                                    order_total += total_price
                                    
                                    # Decrease inventory
                                    inventory.quantity -= quantity
                                    inventory.save()
                        except Exception:
                            pass
                    
                    # Update order total
                    order.total_amount = order_total
                    order.save()
                    orders.append(order)
                
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {num_orders} orders with items'))

                # Step 8: Create Payments for orders
                self.stdout.write('Creating payments...')
                payments_created = 0
                for order in orders:
                    # Create payment for non-pending orders
                    if order.status != OrderStatus.PENDING_PAYMENT:
                        status_map = {
                            OrderStatus.PROCESSING: Payment.PaymentStatus.SUCCESS,
                            OrderStatus.COMPLETED: Payment.PaymentStatus.SUCCESS,
                            OrderStatus.PAYMENT_FAILED: Payment.PaymentStatus.FAILED,
                            OrderStatus.CANCELLED: Payment.PaymentStatus.CANCELLED,
                        }
                        payment_status = status_map.get(order.status, Payment.PaymentStatus.PENDING)
                        
                        PaymentFactory(
                            order=order,
                            amount=order.total_amount,
                            status=payment_status
                        )
                        payments_created += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {payments_created} payments'))

                # Step 9: Create Reviews for some products
                self.stdout.write('Creating reviews...')
                reviews_created = 0
                for user in users:
                    # Each user reviews 0-5 products
                    num_reviews = random.randint(0, 5)
                    reviewed_products = random.sample(products, min(num_reviews, len(products)))
                    
                    for product in reviewed_products:
                        try:
                            ReviewFactory(
                                user=user,
                                product=product,
                                is_verified_purchase=random.choice([True, False])
                            )
                            reviews_created += 1
                        except Exception:
                            # Skip if user already reviewed this product (unique constraint)
                            pass
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {reviews_created} reviews'))

                # Step 10: Create Wishlists
                self.stdout.write('Creating wishlists...')
                wishlists_created = 0
                for user in random.sample(users, min(len(users), num_users // 2)):
                    wishlist, created = Wishlist.objects.get_or_create(user=user)
                    # Add 1-10 products to wishlist
                    num_items = random.randint(1, 10)
                    for product in random.sample(products, min(num_items, len(products))):
                        try:
                            WishlistItemFactory(wishlist=wishlist, product=product)
                        except Exception:
                            # Skip if product already in wishlist (unique constraint)
                            pass
                    wishlists_created += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {wishlists_created} wishlists'))

                self.stdout.write(self.style.SUCCESS('\n' + '='*60))
                self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
                self.stdout.write(self.style.SUCCESS('='*60))
                self.stdout.write(self.style.SUCCESS(f'Users: {num_users}'))
                self.stdout.write(self.style.SUCCESS(f'Addresses: {addresses_created}'))
                self.stdout.write(self.style.SUCCESS(f'Categories: {len(all_categories)}'))
                self.stdout.write(self.style.SUCCESS(f'Products: {num_products}'))
                self.stdout.write(self.style.SUCCESS(f'Carts: {carts_created}'))
                self.stdout.write(self.style.SUCCESS(f'Orders: {num_orders}'))
                self.stdout.write(self.style.SUCCESS(f'Payments: {payments_created}'))
                self.stdout.write(self.style.SUCCESS(f'Reviews: {reviews_created}'))
                self.stdout.write(self.style.SUCCESS(f'Wishlists: {wishlists_created}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError during seeding: {str(e)}'))
            raise

    def clear_data(self):
        """Clear all seeded data from the database"""
        # Clear in reverse dependency order
        from apps.wishlist.models import WishlistItem, Wishlist
        from apps.reviews.models import Review
        from apps.payments.models import Payment
        from apps.orders.models import OrderItem, Order
        from apps.cart.models import CartItem, Cart
        from apps.inventory.models import InventoryReservation, InventoryItem
        from apps.products.models import ProductImage, Product, Category
        from apps.accounts.models import Address, UserProfile, User

        WishlistItem.objects.all().delete()
        Wishlist.objects.all().delete()
        Review.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        InventoryReservation.objects.all().delete()
        InventoryItem.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Address.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
