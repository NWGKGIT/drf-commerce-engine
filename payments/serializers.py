from rest_framework import serializers
from .models import Payment
from orders.models import Order

class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    # Callback URL is where Chapa redirects the user after payment (Plug Your Frontend URL If you have one)
    return_url = serializers.URLField(required=True) 

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
            if order.status in ['completed']:
                raise serializers.ValidationError("Order is already paid.")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'reference', 'amount', 'status', 'created_at']
        read_only_fields = ['reference', 'amount', 'status']