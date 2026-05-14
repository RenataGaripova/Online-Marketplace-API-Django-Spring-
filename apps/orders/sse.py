# Python modules
import logging
import redis
import redis.asyncio as aioredis
import json

# Django modules
from django.conf import settings

logger = logging.getLogger(__name__)

ORDER_CHANNEL_PREFIX: str = "order"
TIMEOUT: int = 15


def _channel(order_id: int) -> str:
    return f"{ORDER_CHANNEL_PREFIX}:{order_id}"


def _redis_client() -> redis.Redis:
    return redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)


def publish_order_event(
    order_id: int, status: str, status_display: str
) -> None:
    """Publishes new order events."""
    data = json.dumps({
        "order_id": order_id,
        "status": status,
        "status_display": status_display,
    })
    client: redis.Redis = _redis_client()
    try:
        client.publish(_channel(order_id=order_id), data)
    finally:
        client.close()


async def stream(order_id: int):
    """Async channel subscription used in SSE-view."""
    client: aioredis.Redis = aioredis.from_url(
        settings.REDIS_SSE_URL, decode_responses=True
    )
    pubsub = client.pubsub()
    await pubsub.subscribe(_channel(order_id=order_id))
    try:
        while True:
            msg = await pubsub.get_message(timeout=TIMEOUT)
            if msg is None:
                yield ": keep-alive\n\n"
                continue
            data = msg.get("data")
            if data:
                yield f"data: {data}\n\n"
    finally:
        try:
            await pubsub.unsubscribe(_channel(order_id=order_id))
            await pubsub.aclose()
            await client.aclose()
        except Exception:
            logger.exception(
                "Failed to clean up pubsub for order %s", order_id
            )
