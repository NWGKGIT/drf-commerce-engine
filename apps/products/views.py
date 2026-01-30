from rest_framework import viewsets, permissions
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    
)
from apps.core.permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import viewsets, status


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]  # Adjust later if needed

    def get_queryset(self):
        # Base query with optimization
        qs = Category.objects.prefetch_related(
            "subcategories", "subcategories__subcategories"
        ).order_by("name")

        # ONLY filter for roots if we are viewing the main list.
        # If we are looking at a detail page (retrieve), allow all categories.
        if self.action == "list":
            return qs.filter(parent_category__isnull=True)

        return qs


class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images", "inventory_items")
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    # Enable search and ordering
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'name', 'created_at', 'discount_price']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()

        # Category filtering
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        # Featured filtering
        featured = self.request.query_params.get("featured")
        if featured:
            qs = qs.filter(is_featured=True)

        # Price range filtering
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        return qs


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all().order_by("position")
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


