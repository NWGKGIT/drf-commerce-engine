# inventory/services.py
from django.db import transaction
from django.db.models import F, Sum
from inventory.models import InventoryItem

@transaction.atomic
def deduct_stock(product, quantity):
    inventory_items = (
        InventoryItem.objects
        .filter(product=product)
        .select_for_update()
        .order_by('id') # Deadlock prevention
    )
    
    total_physical = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
    
    if total_physical < quantity:
         raise ValueError(f"Not enough stock. Available: {total_physical}, Requested: {quantity}")

    remaining_to_deduct = quantity
    
    for item in inventory_items:
        if remaining_to_deduct <= 0:
            break
            
        if item.quantity >= remaining_to_deduct:
            item.quantity = F('quantity') - remaining_to_deduct
            item.save(update_fields=['quantity'])
            remaining_to_deduct = 0
        else:
            deducted = item.quantity
            item.quantity = 0
            item.save(update_fields=['quantity'])
            remaining_to_deduct -= deducted

@transaction.atomic
def restore_stock(product, quantity):
    """
    Restores stock to the first available inventory location for a product.
    """
    if quantity <= 0:
        return

    # Find the primary or first location for this product
    inventory_item = InventoryItem.objects.filter(product=product).order_by('id').first()

    if inventory_item:
        inventory_item.quantity = F('quantity') + quantity
        inventory_item.save(update_fields=['quantity'])
    else:
        # Fallback: If no inventory record exists at all, create one in a default location
        InventoryItem.objects.create(product=product, quantity=quantity)