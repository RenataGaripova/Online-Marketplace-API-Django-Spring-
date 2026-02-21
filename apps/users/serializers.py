# Python modules
from typing import Any

# Django modules
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    IntegerField,
    Serializer,
    ValidationError
)
from rest_framework.validators import UniqueValidator

# Project modules
from .models import CustomUser, Address


# GET

class AddressSerializer(ModelSerializer):
    """Serializer for address model."""

    class Meta:
        """Metadata."""

        model = Address
        fields = (
            "id",
            "street",
            "city",
            "state",
            "zip_code"
        )


class UserBaseSerializer(ModelSerializer):
    """Base user serializer to handle list and retrieve actions."""

    class Meta:
        """Metadata."""

        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "birth_date",
            "is_seller",
        )


class UserDetailedSerializer(ModelSerializer):
    """User serializer to retrieve detailed information."""

    total_reviews = IntegerField()
    addresses = AddressSerializer(man=True)

    class Meta:
        """Metadata."""

        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "birth_date",
            "is_seller",
            "total_reviews",
            "addresses",
        )


# POST

class UserCreateSerializer(ModelSerializer):
    """Serializer for creating users."""

    password = CharField(
        max_length=CustomUser.MAX_PASSWORD_LENGTH,
        required=True,
        write_only=True,
    )

    class Meta:
        """Metadata."""
        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "birth_date",
            "is_seller",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserResetPasswordSerializer(Serializer):
    """Serializer for password reset."""

    current_password = CharField(
        max_length=CustomUser.MAX_PASSWORD_LENGTH,
        required=True,
        write_only=True,
    )
    new_password = CharField(
        max_length=CustomUser.MAX_PASSWORD_LENGTH,
        required=True,
        write_only=True,
    )

    def validate_current_password(
        self,
        value: str,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> str:
        """Validates current password."""

        user = self.context.get("request").user
        if not user.check_password(value):
            raise ValidationError("Wrong password.")
        return value

    def validate_new_password(
        self,
        value: str,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> str:
        """Validates new password."""

        validate_password(value, self.context.get("request"))
        return value

    def save(
        self,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> CustomUser:
        """Saves user's instance."""

        new_password = self.validated_data.pop("new_password")
        user = self.context.get("request").user
        user.set_password(new_password)
        user.save()
        return user


class AddressWriteSerializer(ModelSerializer):
    """Serializer for address model."""

    user = UserBaseSerializer(read_only=True)

    class Meta:
        """Metadata."""

        model = Address
        fields = (
            "id",
            "street",
            "city",
            "state",
            "zip_code"
        )
