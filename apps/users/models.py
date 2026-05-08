from zoneinfo import available_timezones

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
    ForeignKey,
    CASCADE,
)
from django.utils.translation import gettext_lazy as _

from apps.abstracts.models import AbstractBaseModel


class CustomUser(AbstractUser):
    """
    CustomUser database (table) model.
    """

    MAX_PHONE_LENGTH: int = 20
    MAX_EMAIL_LENGTH: int = 20
    MAX_ADDRESS_LENGTH: int = 255
    MAX_LANG_LENGTH: int = 3
    MAX_TIMEZONE_LENGTH: int = 120
    PREFFERED_LANGUAGES = ("en", "ru", "kz")
    TIMEZONES = ((zone, zone) for zone in available_timezones())

    email: EmailField = EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name=_("Email"),
    )
    phone: CharField = CharField(
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        null=True,
        verbose_name=_("Phone number"),
    )
    is_seller: BooleanField = BooleanField(
        default=False,
        verbose_name=_("Is user a seller?"),
    )
    address: CharField = CharField(
        max_length=MAX_ADDRESS_LENGTH,
        blank=True,
        null=True,
        verbose_name=_("Address"),
    )
    preffered_language: CharField = CharField(
        max_length=MAX_LANG_LENGTH,
        choices=[(lang, lang) for lang in PREFFERED_LANGUAGES],
        default="en",
        verbose_name=_("Preffered language"),
        help_text=_("Preffered language"),
    )
    timezone: CharField = CharField(
        max_length=MAX_TIMEZONE_LENGTH,
        choices=TIMEZONES,
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_("Timezone"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    class Meta:
        """Meta class."""

        verbose_name = _("Custom User")
        verbose_name_plural = _("Custom Users")
        ordering: tuple[str, str] = ("-date_joined",)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.email


class Address(AbstractBaseModel):
    """Adress model."""

    CITY_MAX_LENGTH: int = 100
    STREET_MAX_LENGTH: int = 100
    ZIP_MAX_LENGTH: int = 100

    user: ForeignKey = ForeignKey(
        "users.CustomUser", on_delete=CASCADE, related_name="addresses"
    )
    city: CharField = CharField(
        max_length=CITY_MAX_LENGTH,
        verbose_name=_("City"),
    )
    street: CharField = CharField(
        max_length=STREET_MAX_LENGTH,
        verbose_name=_("Street"),
    )
    zip_code: CharField = CharField(
        max_length=ZIP_MAX_LENGTH,
        verbose_name=_("Postal zip code"),
    )
    is_default: CharField = BooleanField(
        default=False,
        verbose_name=_("Is default address?"),
    )

    class Meta:
        """Meta class."""

        verbose_name = _("Address")
        verbose_name_plural = _("Address")
        ordering: tuple[str, ...] = ("-created_at",)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return f"{self.city}, {self.street}"
