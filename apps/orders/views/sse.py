# Python modules
import json
from asgiref.sync import sync_to_async

# Django modules
from django.http.response import (
    Http404,
    HttpResponseForbidden,
    StreamingHttpResponse,
)

# DRF modules
from django.http import HttpRequest
from django.http.response import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

# Project modules
from apps.orders.models import Order
from apps.orders.sse import stream


async def order_status_stream(request: HttpRequest, order_id: int):
    """Async SSE-stream of an order's status."""
    try:
        user_auth = await sync_to_async(
            JWTAuthentication().authenticate, thread_sensitive=False
        )(request)
    except AuthenticationFailed as e:
        return JsonResponse(
            data={"detail": str(e)}, status=HTTP_401_UNAUTHORIZED
        )
    if user_auth is None:
        return JsonResponse(
            data={"detail": "Login first."}, status=HTTP_401_UNAUTHORIZED
        )
    user, _ = user_auth
    try:
        order = await Order.objects.only("id", "user_id", "status").aget(
            pk=order_id
        )
    except Order.DoesNotExist:
        raise Http404
    if order.user_id != user.id:
        return HttpResponseForbidden("Order is not yours.")

    async def event_stream():
        yield ": connected\n\n"
        data_initial = json.dumps({
            "order_id": order.id,
            "status": order.status,
            "status_display": order.get_status_display(),
        })
        yield f"event: status\ndata: {data_initial}\n\n"
        async for chunk in stream(order.id):
            yield chunk

    response: StreamingHttpResponse = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
