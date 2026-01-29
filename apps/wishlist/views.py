from rest_framework import viewsets, permissions, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from .models import Wishlist, WishlistItem
from .serializers import WishlistItemSerializer, WishlistSerializer

class WishlistViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_object(self):
        obj, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return obj

class WishlistItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return WishlistItem.objects.filter(wishlist__user=self.request.user)

    def perform_create(self, serializer):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        serializer.save(wishlist=wishlist)