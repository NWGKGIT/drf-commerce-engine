import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, Sequence
from .models import Category, Product, ProductImage
from django.utils.text import slugify
import random
from faker import Faker as FakerInstance

fake = FakerInstance()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.LazyAttributeSequence(lambda obj, n: f'{fake.word().title()} {fake.word().title()} {n}')
    slug = LazyAttribute(lambda obj: slugify(obj.name))
    description = Faker('sentence')
    is_active = True
    parent_category = None  # Can be overridden to create subcategories


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
    
    category = SubFactory(CategoryFactory)
    name = factory.LazyAttributeSequence(lambda obj, n: f'{fake.word().title()} {fake.word().title()} {n}')
    sku = Sequence(lambda n: f'SKU-{n:06d}')
    slug = LazyAttribute(lambda obj: slugify(obj.sku))
    description = Faker('text', max_nb_chars=500)
    price = Faker('pydecimal', left_digits=4, right_digits=2, positive=True, min_value=10, max_value=9999)
    discount_price = None
    currency = 'ETB'
    specifications = factory.LazyFunction(lambda: {
        'weight': f'{random.randint(100, 5000)}g',
        'dimensions': f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)} cm',
        'color': random.choice(['Red', 'Blue', 'Green', 'Black', 'White', 'Silver']),
        'material': random.choice(['Plastic', 'Metal', 'Wood', 'Glass', 'Fabric'])
    })
    is_featured = Faker('boolean', chance_of_getting_true=20)
    is_active = True


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = ProductImage
    
    product = SubFactory(ProductFactory)
    image_url = Faker('image_url')
    alt_text = LazyAttribute(lambda obj: f'{obj.product.name} image')
    is_main = False
    position = Sequence(lambda n: n)
