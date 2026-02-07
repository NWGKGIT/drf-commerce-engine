import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, Sequence, Iterator, post_generation
from .models import Category, Product, ProductImage
from django.utils.text import slugify
import random
from decimal import Decimal

# Real-world data for seeding
CATEGORIES = [
    "Electronics", "Computers", "Smartphones", "Clothing", "Shoes", 
    "Home & Kitchen", "Books", "Sports & Outdoors", "Beauty & Care", "Toys & Games"
]

PRODUCT_DATA = [
    ("Electronics", "Sony WH-1000XM5 Noise Canceling Headphones", 348.00),
    ("Electronics", "Samsung 55-Inch Class Crystal UHD 4K Smart TV", 497.99),
    ("Electronics", "GoPro HERO11 Black", 399.99),
    ("Computers", "Apple MacBook Pro 16-inch M2 Max", 3499.00),
    ("Computers", "Dell XPS 13 Plus Laptop", 1399.00),
    ("Computers", "Logitech MX Master 3S Wireless Mouse", 99.99),
    ("Smartphones", "Apple iPhone 14 Pro Max (256GB)", 1199.00),
    ("Smartphones", "Samsung Galaxy S23 Ultra", 1199.99),
    ("Smartphones", "Google Pixel 7 Pro", 899.00),
    ("Clothing", "Levi's Men's 501 Original Fit Jeans", 59.50),
    ("Clothing", "Hanes Men's EcoSmart Fleece Hooded Sweatshirt", 22.00),
    ("Shoes", "Nike Air Force 1 '07", 110.00),
    ("Shoes", "Adidas Ultraboost Light Running Shoes", 190.00),
    ("Home & Kitchen", "Instant Pot Duo 7-in-1 Electric Pressure Cooker", 99.95),
    ("Home & Kitchen", "Keurig K-Elite Coffee Maker", 149.00),
    ("Books", "Atomic Habits by James Clear", 13.79),
    ("Books", "The Psychology of Money by Morgan Housel", 12.99),
    ("Sports & Outdoors", "Yoga Mat Non Slip", 25.99),
    ("Sports & Outdoors", "Fitbit Charge 5 Activity Tracker", 129.95),
]


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = Iterator(CATEGORIES)
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    description = Faker('paragraph', nb_sentences=2)
    is_active = True
    parent_category = None


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ('name',)
        exclude = ('_data',)

    _data = Iterator(PRODUCT_DATA)

    category = LazyAttribute(lambda obj: Category.objects.get_or_create(name=obj._data[0])[0])
    name = LazyAttribute(lambda obj: obj._data[1])
    
    # Calculate price (multiply by 100 for ETB rough conversion)
    price = LazyAttribute(lambda obj: Decimal(str(obj._data[2])) * 100)
    
    sku = Sequence(lambda n: f'SKU-{n:06d}')
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    description = Faker('text', max_nb_chars=800)
    
    currency = 'ETB'

    specifications = factory.LazyFunction(lambda: {
        'weight': f'{random.randint(100, 5000)}g',
        'dimensions': f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)} cm',
        'color': random.choice(['Black', 'White', 'Silver', 'Blue', 'Red']),
        'material': random.choice(['Plastic', 'Metal', 'Glass', 'Fabric'])
    })
    is_featured = Faker('boolean', chance_of_getting_true=20)
    is_active = True


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = SubFactory(ProductFactory)
    image_url = Faker('image_url', width=800, height=800)
    alt_text = LazyAttribute(lambda obj: f'{obj.product.name} view')
    is_main = False
