# Python modules
from typing import (
    Type,
    Any,
    Optional,
)

# Django modules
from django.db.models import QuerySet, Manager

# DRF modules
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import Serializer
from rest_framework.pagination import BasePagination
from rest_framework.status import (
    HTTP_200_OK,
)


class DRFResponseMixin:
    """Mixin to return DRF responses."""

    def get_drf_response(
        self,
        request: DRFRequest,
        data: QuerySet | Manager,
        serializer_class: Type[Serializer],
        many: bool,
        limit: Optional[int] = None,
        paginator: Optional[BasePagination] = None,
        serializer_context: Optional[dict[str, Any]] = None,
        status_code: int = HTTP_200_OK,
    ) -> DRFResponse:
        """Returns DRF response."""
        if not serializer_context:
            serializer_context = {"request": request}
        if paginator and many:
            if limit is not None:
                paginator.page_size = limit
            objects: list = paginator.paginate_queryset(
                queryset=data,
                request=request,
                view=self,
            )
            serializer: Serializer = serializer_class(
                objects,
                many=True,
                context=serializer_context,
            )
            return paginator.get_paginated_response(serializer.data)
        serializer: Serializer = serializer_class(
            data,
            many=many,
            context=serializer_context,
        )
        return DRFResponse(data=serializer.data, status=status_code)
