from rest_framework import serializers

from apps.orders.models import Order, OrderStatus

from .models import Payment


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    # Callback URL is where Chapa redirects the user after payment.
    return_url = serializers.URLField(required=True)

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            if order.status == OrderStatus.COMPLETED:
                raise serializers.ValidationError("Order is already paid.")
            if order.status == OrderStatus.CANCELLED:
                raise serializers.ValidationError("Order has been cancelled.")
            if order.status == OrderStatus.PROCESSING:
                raise serializers.ValidationError("Order is already processing.")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'reference', 'amount', 'status', 'created_at']
        read_only_fields = ['reference', 'amount', 'status']
