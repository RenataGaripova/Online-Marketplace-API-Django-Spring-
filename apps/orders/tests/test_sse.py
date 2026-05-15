"""Tests for the SSE order-status endpoint."""
import asyncio
import json
from typing import AsyncIterator, Tuple

import pytest
import redis
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.http import HttpRequest
from django.test import RequestFactory
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.orders.models import Order
from apps.orders.signals import publish_status_change
from apps.orders.sse import publish_order_event
from apps.orders.views.sse import order_status_stream
from apps.users.models import Address

User = get_user_model()


def _redis_alive() -> bool:
    try:
        from django.conf import settings as dj

        client = redis.from_url(dj.REDIS_SSE_URL, decode_responses=True)
        client.ping()
        client.close()
        return True
    except Exception:  # noqa: BLE001
        return False


redis_required = pytest.mark.skipif(
    not _redis_alive(),
    reason="Redis is not running on REDIS_SSE_URL.",
)


@pytest.fixture(autouse=True)
def _disconnect_signal():
    """Keep tests independent of Celery — disable the post_save publisher."""
    post_save.disconnect(publish_status_change, sender=Order)
    yield
    post_save.connect(publish_status_change, sender=Order)


@pytest.fixture
def jwt_user(db) -> Tuple[User, Order, str]:
    user = User.objects.create_user(
        username="sse_user", email="sse@example.com", password="pw"
    )
    addr = Address.objects.create(
        user=user, city="C", street="S 1", zip_code="000001"
    )
    order = Order.objects.create(
        user=user,
        phone_number="+1234567890",
        delivery_address=addr,
        status="P",
    )
    token = str(RefreshToken.for_user(user).access_token)
    return user, order, token


def _build_request(method: str, path: str, token: str | None = None) -> HttpRequest:
    factory = RequestFactory()
    headers = {}
    if token is not None:
        headers["HTTP_AUTHORIZATION"] = f"JWT {token}"
    return factory.generic(method, path, **headers)


async def _drain(
    response_iter: AsyncIterator[bytes], expected_events: int, timeout: float = 3.0
) -> list[str]:
    """Collect a fixed number of SSE messages (separated by blank lines)."""
    collected: list[str] = []
    buffer = ""
    deadline = asyncio.get_event_loop().time() + timeout
    async for chunk in response_iter:
        text = chunk.decode() if isinstance(chunk, (bytes, bytearray)) else chunk
        buffer += text
        while "\n\n" in buffer:
            msg, buffer = buffer.split("\n\n", 1)
            collected.append(msg + "\n\n")
            if len(collected) >= expected_events:
                return collected
        if asyncio.get_event_loop().time() > deadline:
            break
    return collected


@pytest.mark.django_db
class TestSseUrlRouting:
    """The SSE endpoint must require an order_id in the URL."""

    def test_reverse_requires_order_id(self):
        url = reverse("order-status-stream", kwargs={"order_id": 42})
        assert url == "/api/v1/orders/42/stream/"

    def test_old_unparametrized_path_404s(self, client):
        response = client.get("/api/v1/orders/stream/")
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
class TestSseAuth:
    def test_no_token_returns_401(self, jwt_user):
        _, order, _ = jwt_user
        request = _build_request("GET", f"/api/v1/orders/{order.id}/stream/")
        response = asyncio.run(order_status_stream(request, order_id=order.id))
        assert response.status_code == 401
        assert b"Login first" in response.content

    def test_bad_token_returns_401(self, jwt_user):
        _, order, _ = jwt_user
        request = _build_request(
            "GET", f"/api/v1/orders/{order.id}/stream/", token="not-a-jwt"
        )
        response = asyncio.run(order_status_stream(request, order_id=order.id))
        assert response.status_code == 401

    def test_other_users_order_returns_403(self, jwt_user):
        _, order, _ = jwt_user
        other = User.objects.create_user(
            username="other", email="o@example.com", password="pw"
        )
        other_token = str(RefreshToken.for_user(other).access_token)
        request = _build_request(
            "GET",
            f"/api/v1/orders/{order.id}/stream/",
            token=other_token,
        )
        response = asyncio.run(order_status_stream(request, order_id=order.id))
        assert response.status_code == 403

    def test_missing_order_returns_404(self, jwt_user):
        user, _order, token = jwt_user
        request = _build_request(
            "GET", "/api/v1/orders/999999/stream/", token=token
        )
        with pytest.raises(Exception) as exc_info:
            asyncio.run(order_status_stream(request, order_id=999_999))
        # The view raises Http404 — Django converts it to 404 in middleware,
        # but here we call the view directly so the exception escapes.
        from django.http import Http404

        assert isinstance(exc_info.value, Http404)


@pytest.mark.django_db(transaction=True)
class TestSseStreaming:
    """End-to-end: status snapshot on connect, then a published event."""

    @redis_required
    def test_streams_initial_snapshot(self, jwt_user):
        _, order, token = jwt_user
        request = _build_request(
            "GET", f"/api/v1/orders/{order.id}/stream/", token=token
        )

        async def run():
            response = await order_status_stream(request, order_id=order.id)
            assert response.status_code == 200
            assert response["Content-Type"] == "text/event-stream"
            assert response["X-Accel-Buffering"] == "no"
            assert response["Cache-Control"] == "no-cache"
            messages = await _drain(
                response.streaming_content, expected_events=2, timeout=2.0
            )
            await response.streaming_content.aclose()
            return messages

        messages = asyncio.run(run())

        # First frame: the connection comment.
        assert messages[0].startswith(": connected"), messages
        # Second frame: the initial status event in proper SSE format.
        assert messages[1].startswith("event: status\ndata: "), messages[1]
        payload = json.loads(messages[1].split("data: ", 1)[1].strip())
        assert payload == {
            "order_id": order.id,
            "status": "P",
            "status_display": "Processing",
        }

    @redis_required
    def test_streams_published_event(self, jwt_user):
        _, order, token = jwt_user
        request = _build_request(
            "GET", f"/api/v1/orders/{order.id}/stream/", token=token
        )
        channel = f"order:{order.id}"

        from django.conf import settings as dj

        def _wait_for_subscriber():
            """Block until the SSE view actually subscribes to the channel."""
            client = redis.from_url(dj.REDIS_SSE_URL, decode_responses=True)
            try:
                for _ in range(50):
                    counts = client.execute_command("PUBSUB", "NUMSUB", channel)
                    if counts and int(counts[1]) >= 1:
                        return True
                    import time

                    time.sleep(0.05)
                return False
            finally:
                client.close()

        async def run():
            response = await order_status_stream(request, order_id=order.id)
            iterator = response.streaming_content

            # Drive the generator one chunk at a time until subscribe lands.
            initial_chunks: list[str] = []
            buffer = ""
            async for chunk in iterator:
                text = chunk.decode() if isinstance(chunk, bytes) else chunk
                buffer += text
                while "\n\n" in buffer:
                    msg, buffer = buffer.split("\n\n", 1)
                    initial_chunks.append(msg + "\n\n")
                if len(initial_chunks) >= 2:
                    break

            # Now the generator is paused after the initial status frame;
            # the next iteration will enter stream() and run subscribe().
            # Schedule the publish on a thread that waits for subscribe first.
            async def publish_after_subscribe():
                ok = await asyncio.to_thread(_wait_for_subscriber)
                assert ok, "subscriber never appeared"
                await asyncio.to_thread(
                    publish_order_event, order.id, "S", "Shipped"
                )

            publisher_task = asyncio.create_task(publish_after_subscribe())

            tail = await _drain(iterator, expected_events=1, timeout=5.0)
            await publisher_task
            await iterator.aclose()
            return tail

        tail = asyncio.run(run())
        assert tail, "no event delivered after publish"
        frame = tail[0]
        assert frame.startswith("data: "), frame
        payload = json.loads(frame.split("data: ", 1)[1].strip())
        assert payload == {
            "order_id": order.id,
            "status": "S",
            "status_display": "Shipped",
        }


@pytest.mark.django_db(transaction=True)
class TestSseAcceptHeader:
    """The endpoint must serve clients sending Accept: text/event-stream.

    Earlier the view was wrapped in @api_view, which made DRF respond 406
    for the standard SSE Accept header — this regression check keeps that
    from coming back.
    """

    @redis_required
    def test_accept_event_stream_is_not_406(self, jwt_user):
        _, order, token = jwt_user
        request = _build_request(
            "GET", f"/api/v1/orders/{order.id}/stream/", token=token
        )
        request.META["HTTP_ACCEPT"] = "text/event-stream"

        async def run():
            response = await order_status_stream(request, order_id=order.id)
            try:
                assert response.status_code == 200
                assert response["Content-Type"] == "text/event-stream"
            finally:
                if hasattr(response, "streaming_content"):
                    await response.streaming_content.aclose()

        asyncio.run(run())
