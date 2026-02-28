from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    CustomUser database (table) model.
    """
    MAX_EMAIL_LENGTH = 20
    MAX_ADDRESS_LENGTH = 255

    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=MAX_EMAIL_LENGTH,
        blank=True,
        null=True
    )
    is_seller = models.BooleanField(default=False)
    address = models.CharField(
        max_length=MAX_ADDRESS_LENGTH,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.email
