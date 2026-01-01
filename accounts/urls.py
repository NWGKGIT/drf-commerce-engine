from django.urls import path, include
from .views import get_csrf_token
from rest_framework.routers import DefaultRouter
from accounts.views import AddressViewSet

router = DefaultRouter()
router.register(r"addresses", AddressViewSet, basename="address")
urlpatterns = [
    path("csrf/", get_csrf_token, name="get-csrf"), #use this to get a valid csrf token when testing in postman
    path("", include(router.urls)),
]
