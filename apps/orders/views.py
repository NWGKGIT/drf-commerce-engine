from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer, OrderStatusUpdateSerializer
from .services import create_order_from_cart, cancel_order

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    serializer_class = OrderSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by("-created_at")
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action in ["partial_update", "update"]:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can update order status."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        address_id = request.data.get("address_id")

        try:
            order = create_order_from_cart(user=request.user, address_id=address_id)
        except DjangoValidationError as e:
            raise DRFValidationError({"detail": e.messages})
        except ValueError as e:
            raise DRFValidationError({"detail": str(e)})

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Endpoint to cancel an order.
        POST /api/orders/{id}/cancel/
        """
        order = self.get_object()
        
        user_initiated = not request.user.is_staff
        
        try:
            cancel_order(order, user_initiated=user_initiated)
            return Response({"status": "Order cancelled successfully."})
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)