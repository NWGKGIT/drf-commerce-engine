from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r"items", CartItemViewSet, basename="cart-items")


urlpatterns = [
    path("my_cart/", CartViewSet.as_view({"get": "my_cart"}), name="my-cart"),
    path("", include(router.urls)),
]
