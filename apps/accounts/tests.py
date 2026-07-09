import pytest
from rest_framework import status


@pytest.mark.django_db
def test_admin_setup_without_token_is_service_unavailable(settings, client):
    settings.INITIAL_ADMIN_TOKEN = None

    response = client.post(
        "/api/accounts/admin-setup/",
        {
            "setup_token": "anything",
            "email": "admin@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        },
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"error": "Admin setup is not configured."}


@pytest.mark.django_db
def test_admin_setup_creates_verified_superuser(settings, client, django_user_model):
    settings.INITIAL_ADMIN_TOKEN = "setup-secret"

    response = client.post(
        "/api/accounts/admin-setup/",
        {
            "setup_token": "setup-secret",
            "email": "admin@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        },
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = django_user_model.objects.get(email="admin@example.com")
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.emailaddress_set.filter(email="admin@example.com", verified=True).exists()
