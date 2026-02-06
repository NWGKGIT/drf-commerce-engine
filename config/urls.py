from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

api_urlpatterns = [
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("wishlist/", include("apps.wishlist.urls")),
    path("payments/", include("apps.payments.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.products.urls")),
]
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
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
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        lambda r, uidb64, token: HttpResponse(
            "Post the new password to /api/auth/password/reset/confirm/"
        ),
        name="password_reset_confirm",
    ),
]
