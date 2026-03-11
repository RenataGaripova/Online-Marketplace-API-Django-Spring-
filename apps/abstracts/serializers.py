from rest_framework.serializers import (
    Serializer,
    IntegerField,
    CharField,
    DateField,
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
