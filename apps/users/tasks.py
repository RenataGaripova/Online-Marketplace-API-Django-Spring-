# Python modules
import logging
import random
import string

# Celery modules
from celery import shared_task

# Django modules
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone


logger = logging.getLogger("users")


OTP_CACHE_KEY = "otp:{email}"
OTP_TTL_SECONDS = 5 * 60


def _otp_key(email: str) -> str:
    return OTP_CACHE_KEY.format(email=email.lower())


@shared_task
def send_welcome_email(user_id: int) -> str:
    """Delayed task: send a welcome email after user registration."""
    from apps.users.models import CustomUser

    user = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        logger.warning("send_welcome_email: user %s not found", user_id)
        return "user_not_found"

    send_mail(
        subject="Welcome to Online Marketplace!",
        message=(
            f"Hi {user.username}, thanks for joining Online Marketplace."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
    logger.info("Welcome email queued for %s", user.email)
    return "sent"


@shared_task
def send_otp_email(email: str) -> str:
    """Delayed task: generate an OTP, store it in Redis and email it."""
    code = "".join(random.choices(string.digits, k=6))
    cache.set(_otp_key(email), code, timeout=OTP_TTL_SECONDS)

    send_mail(
        subject="Your one-time code",
        message=f"Your OTP code is: {code} (valid for 5 minutes).",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
    logger.info("OTP sent to %s", email)
    return "sent"


@shared_task
def cleanup_expired_tokens() -> int:
    """Periodic task: drop expired JWT tokens from the blacklist tables."""
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

    expired_qs = OutstandingToken.objects.filter(expires_at__lt=timezone.now())
    count = expired_qs.count()
    expired_qs.delete()
    logger.info("cleanup_expired_tokens: removed %s expired tokens", count)
    return count
