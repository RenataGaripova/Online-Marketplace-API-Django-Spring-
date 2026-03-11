from django.contrib.auth.models import AbstractUser
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
    ForeignKey,
    CASCADE,
)

from apps.abstracts.models import AbstractBaseModel


class CustomUser(AbstractUser):
    """
    CustomUser database (table) model.
    """

    MAX_PHONE_LENGTH: int = 20
    MAX_EMAIL_LENGTH: int = 20
    MAX_ADDRESS_LENGTH: int = 255

    email: EmailField = EmailField(unique=True, max_length=MAX_EMAIL_LENGTH)
    phone: CharField = CharField(
        max_length=MAX_PHONE_LENGTH, blank=True, null=True
    )
    is_seller: BooleanField = BooleanField(default=False)
    address: CharField = CharField(
        max_length=MAX_ADDRESS_LENGTH, blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.email


class Address(AbstractBaseModel):
    """Adress model."""

    user: ForeignKey = ForeignKey(
        "users.CustomUser", on_delete=CASCADE, related_name="addresses"
    )
    city: CharField = CharField(max_length=100)
    street: CharField = CharField(max_length=100)
    zip_code: CharField = CharField(max_length=10)
    is_default: CharField = BooleanField(default=False)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return f"{self.city}, {self.street}"
