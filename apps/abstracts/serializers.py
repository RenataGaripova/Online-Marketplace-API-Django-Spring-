# Python modules
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime

# Django modules
from django.utils import timezone

# DRF modules
from rest_framework.serializers import (
    Serializer,
    IntegerField,
    CharField,
    DateField,
    SerializerMethodField,
)

# ----------------------------------------------
# DOCS SERIALIZERS
#


class ResponseUserRegistrationSerializer(Serializer):
    """Serializer for user registration."""

    id: IntegerField = IntegerField()
    email: CharField = CharField
    username: CharField = CharField()
    first_name: CharField = CharField()
    last_name: CharField = CharField()
    date_joined: DateField = DateField()
    refresh: CharField = CharField()
    access: CharField = CharField()

    class Meta:
        fields: tuple[str, ...] = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "refresh",
            "access",
        )


class RefreshSerializer(Serializer):
    """Serializer for user registration."""

    refresh: CharField = CharField()

    class Meta:
        fields: tuple[str, ...] = ("refresh",)


class ErrorDetailSerializer(Serializer):
    """Serializer for showing detail's of request's errors."""

    detail: CharField = CharField()

    class Meta:
        fields: tuple[str, ...] = ("detail",)


# ----------------------------------------------
# TIMEZONE SERIALIZERS
#
class TimeZoneSerializerMixin(Serializer):
    """Returns timestamps in user's timezone."""

    created_at: SerializerMethodField = SerializerMethodField()
    updated_at: SerializerMethodField = SerializerMethodField()

    def _get_user_timezone(self) -> ZoneInfo:
        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and getattr(request.user, "timezone", None)
        ):
            try:
                return ZoneInfo(request.user.timezone)
            except ZoneInfoNotFoundError:
                pass
        return ZoneInfo("UTC")

    def get_created_at(self, obj: Any) -> datetime:
        """Returns created_at in client's timezone."""
        return timezone.localtime(obj.created_at, self._get_user_timezone())

    def get_updated_at(self, obj: Any) -> datetime:
        """Returns updated_at in client's timezone."""
        return timezone.localtime(obj.updated_at, self._get_user_timezone())

    def get_deleted_at(self, obj: Any) -> datetime:
        """Returns deleted_at in client's timezone."""
        if obj.deleted_at:
            return timezone.localtime(
                obj.deleted_at, self._get_user_timezone()
            )
        return None
