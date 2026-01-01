from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, ChapaWebhookView

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')

urlpatterns = [
    path('webhook/', ChapaWebhookView.as_view(), name='chapa-webhook'),
    path('', include(router.urls)),
]