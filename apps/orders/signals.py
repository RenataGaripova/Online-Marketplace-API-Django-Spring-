from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.orders.tasks import publish_status_task
from apps.orders.models import Order


@receiver(post_save, sender=Order)
def publish_status_change(
    sender, instance: Order, created: bool, **kwargs
) -> None:
    publish_status_task.delay(
        instance.pk,
        instance.status,
        instance.get_status_display(),
    )
