from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer
from core.permissions import IsEmailVerified
from orders.models import OrderItem, OrderStatus


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEmailVerified]

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
