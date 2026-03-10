from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, CharField, BooleanField


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
