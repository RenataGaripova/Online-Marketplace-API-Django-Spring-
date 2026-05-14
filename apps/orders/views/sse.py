# Python modules
import json

# Django modules
from django.http.response import (
    Http404,
    HttpResponseForbidden,
    StreamingHttpResponse,
)

# DRF modules
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request as DRFRequest

# Project modules
from apps.orders.models import Order
from apps.orders.sse import stream


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def order_status_stream(request: DRFRequest, order_id: int):
    """Async SSE-stream of an order's status."""
    try:
        order = await Order.objects.only("id", "user_id", "status").aget(
            pk=order_id
        )
    except Order.DoesNotExist:
        raise Http404
    if order.user_id != request.user.id:
        return HttpResponseForbidden("Order is not yours.")

    async def event_stream():
        data_initial = json.dumps({
            "order_id": order.id,
            "status": order.status,
            "status_display": order.get_status_display(),
        })
        yield f"event: status\n data: {data_initial}\n\n"
        async for chunk in stream(order.id):
            yield chunk

    response: StreamingHttpResponse = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["X-Accel-Buffering"] = "no"
    return response
