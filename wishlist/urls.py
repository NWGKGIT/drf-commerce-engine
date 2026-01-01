from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet, WishlistItemViewSet

router = DefaultRouter()
router.register(r'items', WishlistItemViewSet, basename='wishlist-items')

urlpatterns = [
    path('my-wishlist/', WishlistViewSet.as_view({'get': 'retrieve'}), name='my-wishlist'),
    path('', include(router.urls)),
]