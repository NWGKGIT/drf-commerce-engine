from django.contrib import admin
from django.urls import path, include
from accounts.views import SecureAdminSetupView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from accounts import urls
from django.http import HttpResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    # DRF Auth Endpoints
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "api/accounts/", include("accounts.urls")
    ),  # account related shit like addresses.
    path("api/", include("products.urls")),
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
    path("api/cart/", include("cart.urls"), name="cart"),
    path("api/auth/init-admin/", SecureAdminSetupView.as_view(), name="init-admin"),
    path("api/orders/", include("orders.urls"), name="orders"),
    path("api/reviews/", include("reviews.urls"), name="reviews"),
    path("api/wishlist/", include("wishlist.urls"), name="wishlist"),
    path("api/payments/", include("payments.urls")),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        lambda r, uidb64, token: HttpResponse("Post the new password to /api/auth/password/reset/confirm/"),
        name="password_reset_confirm",
    ), #crude fix because we don't have a frontend
]
