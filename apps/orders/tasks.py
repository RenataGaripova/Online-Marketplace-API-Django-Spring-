from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_confirmation_email(order_id, user_email):
    send_mail(
        "Order Confirmation",
        f"Your order {order_id} has been confirmed.",
        settings.EMAIL_HOST_USER,
        [user_email],
    )