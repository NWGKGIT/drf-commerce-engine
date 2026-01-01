from rest_framework import serializers
from .models import InventoryReservation, InventoryItem
from django.utils import timezone
from django.db.models import Sum


class InventoryReservationSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    available_quantity = serializers.SerializerMethodField()  
    class Meta:
        model = InventoryReservation
        fields = [
            "id",
            "cart",
            "order",
            "product",
            "product_name",
            "quantity",
            "available_quantity",
            "expires_at",
            "created_at",
        ]

    def get_available_quantity(self, obj):
        total_stock = obj.product.total_quantity
        active_reservations = (
            InventoryReservation.objects.filter(
                product=obj.product, expires_at__gt=timezone.now()
            )
            .exclude(
                id=obj.id
            )  # you shouldn't count your own "hold" as a "taken" item.
            .aggregate(total=Sum("quantity"))
        )

        reserved = active_reservations["total"] or 0
        return total_stock - reserved


class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "location",
            "last_updated",
        ]
