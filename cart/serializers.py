from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from django.db.models import F, Sum
from inventory.models import InventoryReservation, InventoryItem
from django.utils import timezone


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    unit_price = serializers.ReadOnlyField(source="product.price")
    total_price = serializers.SerializerMethodField()
    cart = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "product",
            "product_name",
            "unit_price",
            "quantity",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.quantity * obj.product.price

    def validate(self, data):
        user = self.context["request"].user
        
        if self.instance: 
            product = self.instance.product
            requested_quantity = data.get("quantity", self.instance.quantity)
        else: 
            product = data.get("product")
            requested_quantity = data.get("quantity")

        physical_stock = InventoryItem.objects.filter(product=product).aggregate(
            total=Sum("quantity")
        )["total"] or 0

        cart, _ = Cart.objects.get_or_create(user=user)

        other_reservations_query = InventoryReservation.objects.filter(
            product=product, 
            expires_at__gt=timezone.now()
        ).exclude(cart=cart)
        
        other_reservations = other_reservations_query.aggregate(total=Sum("quantity"))["total"] or 0

        available_to_user = physical_stock - other_reservations

        if requested_quantity > available_to_user:
            raise serializers.ValidationError(
                {
                    "quantity": f"Only {available_to_user} items currently available (including what's in other carts). Requested: {requested_quantity}"
                }
            )

        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "user_email",
            "items",
            "grand_total",
            "created_at",
            "updated_at",
        ]

    def get_grand_total(self, obj):
        return (
            obj.items.aggregate(total=Sum(F("quantity") * F("product__price")))["total"]
            or 0
        )

    extra_kwargs = {"user": {"read_only": True}}
