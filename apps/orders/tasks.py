# Python modules
import logging
from celery import shared_task

# Project modules
from apps.orders.models import Order
from apps.orders.sse import publish_order_event

logger = logging.getLogger(__name__)


@shared_task
def update_order_status(order_id: int, new_status: str) -> None:
    try:
        order: Order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning("Order %s was not found.", order_id)
        return
    if order.status == new_status:
        return
    order.status = new_status
    order.save(update_fields=["status", "updated_at"])
    logger.info("Order #%s progressed to %s", order_id, new_status)


@shared_task
def publish_status_task(
    order_id: int, status: str, status_display: str
) -> None:
    publish_order_event(order_id, status, status_display)
