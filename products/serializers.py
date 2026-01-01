from rest_framework import serializers
from .models import Category, Product, ProductImage
from inventory.serializers import InventoryItemSerializer
from django.db.models import Sum


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    depth = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "parent_category",
            "name",
            "slug",
            "depth",
            "description",
            "is_active",
            "created_at",
            "subcategories",
        ]

    def get_depth(self, obj):
        return self.context.get("depth", 0)

    def get_subcategories(self, obj):
        if hasattr(obj, "subcategories"):
            current_depth = self.context.get("depth", 0)
            context = self.context.copy()
            context["depth"] = current_depth + 1

            return CategorySerializer(
                obj.subcategories.all(), many=True, context=context
            ).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image_url",
            "alt_text",
            "is_main",
            "position",
            "created_at",
        ]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(
        read_only=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)

    final_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    initial_stock = serializers.IntegerField(write_only=True, required=False)

    inventory_items = InventoryItemSerializer(many=True, read_only=True)
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",  # shows the rich object
            "category_id",  # used to send the ID, hidden in GET
            "name",
            "slug",
            "description",
            "sku",
            "price",
            "discount_price",
            "currency",
            "specifications",
            "is_featured",
            "inventory_items",
            "is_active",
            "created_at",
            "updated_at",
            "total_stock",
            "initial_stock",
            "final_price",
            "images",
        ]

    def validate(self, data):
        price = data.get("price")
        discount = data.get("discount_price")

        if price is not None and price < 0:
            raise serializers.ValidationError({"price": "Price cannot be negative."})
        if discount is not None and discount < 0:
            raise serializers.ValidationError(
                {"discount_price": "Discount cannot be negative."}
            )
        if discount is not None and price is not None:
            if discount > price:
                raise serializers.ValidationError(
                    {
                        "discount_price": "Discount price cannot be higher than the original price."
                    }
                )

        return data

    def create(self, validated_data):
        # Pop the stock value
        initial_stock = validated_data.pop("initial_stock", 0)
        
        # Instantiate the Product object WITHOUT saving to DB yet
        product = Product(**validated_data)
        
        # Attach the "secret" attribute needed by the signal
        # Now the instance has this value BEFORE the signal ever fires
        product._initial_stock = initial_stock

        # Save to DB
        # This triggers post_save, which creates the InventoryItem
        # Since _initial_stock is already attached, it will use your value (100)
        product.save()
        return product

    def update(self, instance, validated_data):
        # We ignore initial_stock here because the product already exists.
        # Stock updates should happen via the /inventory/ endpoint instead.
        validated_data.pop("initial_stock", None)
        return super().update(instance, validated_data)

    def get_total_stock(self, obj):
        result = obj.inventory_items.aggregate(total=Sum("quantity"))
        return result["total"] or 0
