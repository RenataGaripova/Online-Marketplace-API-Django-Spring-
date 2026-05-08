# Python modules
from typing import (
    Callable,
    Type,
    TypeVar,
    Any,
    Optional,
)
from functools import wraps

# Django modules
from django.db.models import QuerySet, Manager
from django.utils.translation import gettext as _

# DRF Modules
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

T = TypeVar("T")


def obtain_object_by_pk(
    queryset: QuerySet[T] | Manager[T],
    class_name: Type[T],
    entity_name: str,
) -> Callable:
    """Finds an object in a queryset by it's primary key."""

    def decorator(
        func: Callable[
            [DRFRequest, tuple[Any, ...], dict[Any, Any]], DRFResponse
        ],
    ) -> Callable:
        @wraps(func)
        def wrapper(
            self,
            request: DRFRequest,
            *args: tuple[Any, ...],
            **kwargs: dict[Any, Any],
        ) -> DRFResponse:
            """Finds an object by primary key or returns an error response with details."""
            pk: Optional[str] = str(kwargs.get("pk"))
            if not pk.isdigit():
                return DRFResponse(
                    data={
                        "id": _("%(entity_name)s id must be a number.")
                        % {"entity_name": entity_name}
                    },
                    status=HTTP_400_BAD_REQUEST,
                )
            try:
                kwargs["object"] = queryset.get(pk=int(pk))
                return func(self, request, *args, **kwargs)
            except queryset.model.DoesNotExist:
                return DRFResponse(
                    data={
                        "id": [
                            _(
                                "%(entity_name)s with id '%(pk)s' was not found."
                            )
                            % {"entity_name": entity_name, "pk": pk}
                        ]
                    },
                    status=HTTP_404_NOT_FOUND,
                )
            except queryset.model.MultipleObjectsReturned:
                return DRFResponse(
                    data={
                        "id": [
                            _(
                                "Multiple %(entity_name)s objects were returned for '%(pk)s' id."
                            )
                            % {"entity_name": entity_name, "pk": pk}
                        ]
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

        return wrapper

    return decorator
