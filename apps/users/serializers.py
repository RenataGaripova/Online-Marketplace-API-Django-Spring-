# Python modules
from typing import Any, Optional, Type
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime

# Django modules
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password

# DRF modules
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    Serializer,
)

# Project modules
from apps.users.models import CustomUser, Address
from apps.abstracts.serializers import TimeZoneSerializerMixin


class AddressSerializer(TimeZoneSerializerMixin, ModelSerializer):
    class Meta:
        model: Type[Address] = Address
        fields: str = "__all__"
        read_only_fields: tuple[str, ...] = (
            "id",
            "user",
            "created_at",
            "updated_at",
            "deleted_at",
        )

    def create(self, validated_data: dict[str, Any]) -> Any:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model: CustomUser = CustomUser
        fields: tuple[str, ...] = (
            "id",
            "email",
            "username",
            "phone",
            "is_seller",
        )


class UserRegistrationSerializer(ModelSerializer):
    """Serializer for user registration."""

    password: CharField = CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2: CharField = CharField(write_only=True, required=True)

    class Meta:
        model: CustomUser = CustomUser
        fields: tuple[str, ...] = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password2",
            "date_joined",
        )
        read_only_fields: tuple[str, str] = (
            "id",
            "date_joined",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate that passwords match."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Wrong password."})
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Create a new user with validated data."""
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def get_date_joined(self, obj: CustomUser) -> datetime:
        """Returns date_joined in client's timezone."""
        request = self.context.get("request")
        tz: ZoneInfo = ZoneInfo("UTC")
        if request and request.user.is_authenticated:
            try:
                tz: ZoneInfo = ZoneInfo(request.user.timezone)
            except ZoneInfoNotFoundError:
                tz: ZoneInfo = ZoneInfo("UTC")
        return timezone.localtime(obj.date_joined, tz)


class UserLoginSerializer(Serializer):
    """Serializer for user login."""

    password: CharField = CharField()
    email: CharField = CharField()

    class Meta:
        fields: tuple[str, str] = ("password", "email")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validates user login data."""

        email: str = attrs.get("email")
        password: str = attrs.get("password")

        existing_user: Optional[CustomUser] = CustomUser.objects.filter(
            email=email,
        ).first()

        if not existing_user:
            raise NotFound(
                detail={
                    "email": [f"The user with email: {email} was not found."]
                }
            )

        if not existing_user.check_password(raw_password=password):
            raise ValidationError(detail={"password": "Wrong password."})

        if not existing_user.is_active:
            raise ValidationError(
                detail={"email": "Your account was deactivated."}
            )

        attrs["user"] = existing_user

        return super().validate(attrs=attrs)
