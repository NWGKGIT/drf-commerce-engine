from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

app_name="orders"
router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')

urlpatterns = router.urls