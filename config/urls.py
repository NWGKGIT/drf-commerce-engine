from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path("api/cart/", include("apps.cart.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/", include("apps.products.urls")),
    
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    
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
    
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/wishlist/", include("apps.wishlist.urls")),
    path("api/payments/", include("apps.payments.urls")),
    
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        lambda r, uidb64, token: HttpResponse(
            "Post the new password to /api/auth/password/reset/confirm/"
        ),
        name="password_reset_confirm",
    ),
]