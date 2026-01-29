from django.contrib import admin
from django.urls import path, include
from apps.accounts.views import SecureAdminSetupView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# from apps.accounts import urls
from django.http import HttpResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    # core features
    path("api/cart/", include(("apps.cart.urls", "cart"))),
    path("api/orders/", include(("apps.orders.urls", "orders"))),  # Added missing )
    path("api/inventory/", include(("apps.inventory.urls", "inventory"))),
    path("api/", include(("apps.products.urls", "products"))),
    # DRF Auth Endpoints
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/accounts/", include(("apps.accounts.urls", "accounts"))),
    # account related shit like addresses.
    path("auth/", include("allauth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # path("api/reviews/", include("apps.reviews.urls"), name="reviews"),
    # path("api/wishlist/", include("apps.wishlist.urls"), name="wishlist"),
    # path("api/payments/", include("apps.payments.urls")),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        lambda r, uidb64, token: HttpResponse(
            "Post the new password to /api/auth/password/reset/confirm/"
        ),
        name="password_reset_confirm",
    ),  # crude fix because we don't have a frontend
]
