from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer
from apps.core.permissions import IsEmailVerified
from apps.orders.models import OrderItem, OrderStatus


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product').order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEmailVerified]
    
    # Enable filtering and ordering
    filterset_fields = ['product', 'rating', 'is_verified_purchase']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data["product"]

        if Review.objects.filter(user=self.request.user, product=product).exists():
            raise permissions.PermissionDenied(
                "You have already reviewed this product."
            )

        is_verified = OrderItem.objects.filter(
            order__user=user, order__status=OrderStatus.COMPLETED, product=product
        ).exists()

        serializer.save(user=user, is_verified_purchase=is_verified)
