from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'total_amount', 
            'currency', 'shipping_address_snapshot', 
            'created_at', 'items'
        ]
        read_only_fields = ['order_number', 'total_amount', 'status', 'currency', 'shipping_address_snapshot']

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for Admins to update status.
    """
    class Meta:
        model = Order
        fields = ['status']