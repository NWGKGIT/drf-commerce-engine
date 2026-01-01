from django.db import models
from django.conf import settings
from orders.models import Order
import uuid
class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed',
        CANCELLED = 'cancelled', 'Cancelled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    # Chapa specific fields
    reference = models.CharField(max_length=100, unique=True, help_text="Unique transaction reference for Chapa")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='ETB')
    
    # Tracking
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    provider = models.CharField(max_length=20, default='chapa')
    
    # OPTIONAL: Store full API response for debugging later
    raw_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pay {self.reference} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.reference:
            # Generate a unique ref: TX-ORDERID-UUID
            # This allows multiple payment attempts for one order
            short_uuid = uuid.uuid4().hex[:6].upper()
            self.reference = f"TX-{self.order.order_number}-{short_uuid}"
        super().save(*args, **kwargs)