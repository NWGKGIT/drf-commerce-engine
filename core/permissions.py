from rest_framework import permissions
from allauth.account.models import EmailAddress


class IsEmailVerified(permissions.BasePermission):
    """
    Global permission: Only allows users who have verified their email.
    """

    message = "Email verification required."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True

        return EmailAddress.objects.filter(user=request.user, verified=True).exists()


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )
