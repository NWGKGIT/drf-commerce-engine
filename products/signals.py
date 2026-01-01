from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Category, Product
from inventory.models import InventoryItem

def create_unique_slug(instance, new_slug=None):
    """
    Recursive function to check for slug uniqueness.
    If 'gaming-laptops' exists, it tries 'gaming-laptops-1', then 'gaming-laptops-2', etc.
    """
    slug = new_slug or slugify(instance.name)
    model_class = instance.__class__
    
    qs = model_class.objects.filter(slug=slug).exclude(id=instance.id)
    
    if qs.exists():
        # Conflict found: append a random string or increment number
        new_slug = f"{slug}-{qs.count() + 1}"
        return create_unique_slug(instance, new_slug=new_slug)
    
    return slug

@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=Product)
def generate_slug_on_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(instance)


@receiver(post_save, sender=Product)
def create_product_inventory(sender, instance, created, **kwargs):
    if created:
        stock_value = getattr(instance, "_initial_stock", 0)
        InventoryItem.objects.create(product=instance, quantity=stock_value)