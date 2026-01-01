# accounts/views.py
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Address
from .serializers import AddressSerializer, AdminSetupSerializer
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from core.permissions import IsEmailVerified
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from django.utils.crypto import constant_time_compare
from django.db import transaction

User = get_user_model()


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        # STRICT FILTER: Only return addresses belonging to the logged-in user
        return Address.objects.filter(user=self.request.user).order_by("-is_default")

    def perform_create(self, serializer):
        # logic: if this is the user's first address, make it default automatically
        is_first_address = not Address.objects.filter(user=self.request.user).exists()

        if is_first_address:
            serializer.save(user=self.request.user, is_default=True)
        else:
            # If the user is setting this new address as default,
            # we must unset their previous default.
            if serializer.validated_data.get("is_default", False):
                self._unset_other_defaults()
            serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # If setting as default, unset others first
        if serializer.validated_data.get("is_default", False):
            self._unset_other_defaults()
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You cannot delete this address.")
        super().perform_destroy(instance)

    def _unset_other_defaults(self):
        """Helper to ensure only one address is default at a time."""
        Address.objects.filter(user=self.request.user, is_default=True).update(
            is_default=False
        )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


@method_decorator(sensitive_post_parameters("password", "setup_token"), name="dispatch")
class SecureAdminSetupView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=AdminSetupSerializer,
        responses={201: None},
        description="Initialize the first superuser using a secure token.",
    )
    def post(self, request):
        serializer = AdminSetupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        setup_token = validated_data.get("setup_token")
        if not constant_time_compare(setup_token, settings.INITIAL_ADMIN_TOKEN):
            return Response(
                {"error": "Invalid setup token."}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            with transaction.atomic():
                if User.objects.filter(is_superuser=True).exists():
                    return Response(
                        {"error": "Admin already initialized."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                user = User.objects.create_superuser(
                    email=validated_data["email"], password=validated_data["password"]
                )
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=validated_data["email"],
                    verified=True,
                    primary=True,
                )
            return Response(
                {"message": "Admin account created."}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
