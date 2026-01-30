from django.db import models
from apps.accounts.models import User
from apps.products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', db_index=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('user', 'product')
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['product', 'is_verified_purchase']),
        ]
        
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.id}"