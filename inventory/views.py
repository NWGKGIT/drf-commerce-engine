from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import InventoryReservation, InventoryItem
from .serializers import InventoryReservationSerializer, InventoryItemSerializer
from products.models import Product


class InventoryReservationViewSet(viewsets.ModelViewSet):
    """
    Handles viewing reservations.
    """

    queryset = InventoryReservation.objects.all()
    serializer_class = InventoryReservationSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def check_stock(self, request):
        """
        Public endpoint to check if enough stock exists for a product
        before adding to cart.
        """
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            inventory = InventoryItem.objects.get(product=product)
            actual_stock = inventory.quantity
        except InventoryItem.DoesNotExist:
            actual_stock = 0

        active_reservations = InventoryReservation.objects.filter(
            product=product, expires_at__gt=timezone.now()
        )

        # We exclude the current user's cart reservations from this check so they don't block themselves
        current_cart_id = request.data.get("cart_id")
        if current_cart_id:
            active_reservations = active_reservations.exclude(cart_id=current_cart_id)

        reserved_quantity = sum(r.quantity for r in active_reservations)
        available_quantity = actual_stock - reserved_quantity

        if available_quantity >= quantity:
            return Response({"available": True, "stock_left": available_quantity})
        else:
            return Response(
                {"available": False, "stock_left": available_quantity},
                status=status.HTTP_400_BAD_REQUEST,
            )


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAdminUser]
