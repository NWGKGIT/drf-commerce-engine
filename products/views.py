from rest_framework import viewsets, permissions
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    
)
from core.permissions import IsAdminOrReadOnly
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
        .prefetch_related("images")
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        # Optional filters
        category = self.request.query_params.get("category")
        featured = self.request.query_params.get("featured")
        search = self.request.query_params.get("search")

        if category:
            qs = qs.filter(category__slug=category)

        if featured:
            qs = qs.filter(is_featured=True)

        if search:
            qs = qs.filter(name__icontains=search)

        return qs


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all().order_by("position")
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


