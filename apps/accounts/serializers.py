from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from django.db import transaction
from django.contrib.auth import authenticate, get_user_model
from .models import UserProfile, Address
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["birth_date", "profile_picture", "preferences"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "address_line_1",
            "address_line_2",
            "city",
            "region",
            "postal_code",
            "country",
            "location_pin",
            "is_default",
        ]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        # Automatically assign the address to the request user
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


# --------------------------
# 2. Custom Registration
# --------------------------


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        return data

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        user.save()
        return user


class CustomLoginSerializer(LoginSerializer):
    username = None  # very important
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def _validate_email(self, email, password):
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        return user

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = self._validate_email(email, password)
        else:
            raise serializers.ValidationError("Email and password are required.")

        attrs["user"] = user
        return attrs


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for the user to view/update their own details.
    Includes nested Profile and Address data.
    """

    profile = UserProfileSerializer(required=False)
    # Return limited addresses or a link to them (optional strategy)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile",
            "addresses",
        ]
        read_only_fields = [
            "id",
            "email",
        ]  # Email usually requires a specific flow to change

    @transaction.atomic
    def update(self, instance, validated_data):
        # Handle nested profile update
        profile_data = validated_data.pop("profile", None)

        # Update User fields
        instance = super().update(instance, validated_data)

        # Update Profile fields
        if profile_data:
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
        return instance


class AdminSetupSerializer(serializers.Serializer):
    setup_token = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, data):
        # 1. Match Check
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        try:
            validate_password(data.get("password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data
