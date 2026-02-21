# Python modules
from typing import Any

# Django modules
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    BooleanField,
    ForeignKey,
    CASCADE,
    DateField,
    EmailField,
)
from django.core.validators import (
    RegexValidator
)

# Project modules
from apps.abstracts.models import AbstractBaseModel


class CustomUser(AbstractUser):
    """
    CustomUser database (table) model.
    """
    MAX_PHONE_LENGTH = 12
    MAX_USERNAME_LENGTH = 32
    MAX_PASSWORD_LENGTH = 128
    MAX_PHONE_NUMBER_LENGTH = 15

    username = CharField(max_length=MAX_USERNAME_LENGTH, unique=True)
    email = EmailField(unique=True)
    phone_number = CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Phone number must be entered in the format:"
        " '+999999999'. Up to 15 digits allowed.",
    )
    birth_date = DateField(null=True, blank=True)
    is_seller = BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name")

    def activate(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """Activates a user."""
        self.is_active = True
        self.save(update_fields=("is_active",))

    def deactivate(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """Activates a user."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.email


class Address(AbstractBaseModel):
    """Adress model."""

    MAX_STREET_LENGTH = 128
    MAX_CITY_LENGTH = 128
    MAX_STATE_LENGTH = 128
    MAX_CODE_LENGTH = 16

    street = CharField(max_length=MAX_STREET_LENGTH)
    city = CharField(max_length=MAX_CITY_LENGTH)
    state = CharField(max_length=MAX_STATE_LENGTH)
    zip_code = CharField(max_length=MAX_CODE_LENGTH)
    user = ForeignKey(CustomUser, on_delete=CASCADE)

    class Meta:
        """Metadata."""

        default_related_name = "addresses"
        verbose_name_plural = "Addresses"

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return f"{self.state}, {self.city}, {self.street}, {self.zip_code}"
