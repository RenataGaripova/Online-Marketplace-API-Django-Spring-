# Python modules
import logging
from typing import Any

# DRF modules
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_400_BAD_REQUEST,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError

# Django modules
from django.core.cache import cache
from django.db import DatabaseError

# Project modules
from apps.users.models import CustomUser, Address
from apps.users.serializers import (
    BaseUserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    AddressSerializer,
)
from apps.users.tasks import (
    OTP_CACHE_KEY,
    send_otp_email,
    send_welcome_email,
)
from apps.abstracts.serializers import (
    RefreshSerializer,
    ErrorDetailSerializer,
    ResponseUserRegistrationSerializer,
)

logger = logging.getLogger(__name__)


class CustomUserViewSet(ViewSet):
    throttle_scope_map = {
        "register": "register",
        "request_otp": "otp",
        "verify_otp": "otp",
    }

    def get_throttles(self):
        self.throttle_scope = self.throttle_scope_map.get(self.action)
        return super().get_throttles()

    @extend_schema(
        summary="Registrate a new user.",
        tags=["auths"],
        request=UserRegistrationSerializer,
        responses={
            HTTP_201_CREATED: ResponseUserRegistrationSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid request data.",
                response=ErrorDetailSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=ErrorDetailSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(
                description="Server receives too many requests.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("post",),
        detail=False,
        url_path="register",
    )
    def register(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to register a new CustomUser.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing data about created CustomUser and token data.
        """
        logger.info(
            "Registration attempt for email: %s", request.data.get("email")
        )
        try:
            serializer: UserRegistrationSerializer = (
                UserRegistrationSerializer(data=request.data)
            )
            serializer.is_valid(raise_exception=True)
            user: CustomUser = serializer.save()

            send_welcome_email.delay(user.id)

            # Generate JWT tokens
            refresh_token: RefreshToken = RefreshToken.for_user(user)
            access_token: AccessToken = refresh_token.access_token
        except ValidationError:
            logger.exception(
                "Registration for email %s failed with error: %s",
                request.data.get("email"),
                serializer.errors,
            )
            raise
        except TokenError as e:
            logger.exception(
                "JWT generation for email %s failed with error: %s",
                request.data.get("email"),
                e,
            )
            raise
        except DatabaseError as e:
            logger.exception(
                "Databse error occured during %s email's registration: %s",
                request.data.get("email"),
                e,
            )
            raise
        return DRFResponse(
            data={
                **serializer.data,
                "access": str(access_token),
                "refresh": str(refresh_token),
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Log in a user.",
        tags=["auths"],
        request=UserLoginSerializer,
        responses={
            HTTP_200_OK: ResponseUserRegistrationSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid request data.",
                response=ErrorDetailSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=ErrorDetailSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(
                description="Server receives too many requests.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("post",),
        detail=False,
        url_path="login",
    )
    def login(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to login an existing CustomUser.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing data about logged-in CustomUser and token data.
        """
        serializer: UserLoginSerializer = UserLoginSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        user: CustomUser = serializer.validated_data.get("user")

        detail_serializer: BaseUserSerializer = BaseUserSerializer(
            instance=user,
            many=False,
        )
        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token: AccessToken = refresh_token.access_token

        return DRFResponse(
            data={
                **detail_serializer.data,
                "access": str(access_token),
                "refresh": str(refresh_token),
            },
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="Log out a user.",
        tags=["auths"],
        request=RefreshSerializer,
        responses={
            HTTP_200_OK: ErrorDetailSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid request data.",
                response=ErrorDetailSerializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=ErrorDetailSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(
                description="Server receives too many requests.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("post",),
        detail=False,
        url_path="logout",
    )
    def logout(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to logout an existing CustomUser.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse - message containing status of the logout.
        """
        try:
            refresh_token: str = request.data.get("refresh")
            token: RefreshToken = RefreshToken(refresh_token)
            token.blacklist()
            return DRFResponse(
                data={"detail": "Successfully logged out."},
                status=HTTP_200_OK,
            )
        except Exception as e:
            return DRFResponse(
                data={"detail": f"Invalid refresh token. Error message: {e}"},
                status=HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Request a one-time code by email.",
        tags=["auths"],
    )
    @action(methods=("post",), detail=False, url_path="otp/request")
    def request_otp(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """Queue a Celery task that generates an OTP and emails it."""
        email: str = (request.data.get("email") or "").strip().lower()
        if not email:
            return DRFResponse(
                data={"detail": "Email is required."},
                status=HTTP_400_BAD_REQUEST,
            )
        send_otp_email.delay(email)
        return DRFResponse(
            data={"detail": "OTP code has been sent."},
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="Verify a one-time code stored in Redis.",
        tags=["auths"],
    )
    @action(methods=("post",), detail=False, url_path="otp/verify")
    def verify_otp(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """Compare a submitted OTP against the value cached in Redis."""
        email: str = (request.data.get("email") or "").strip().lower()
        code: str = (request.data.get("code") or "").strip()
        if not email or not code:
            return DRFResponse(
                data={"detail": "Email and code are required."},
                status=HTTP_400_BAD_REQUEST,
            )
        cached = cache.get(OTP_CACHE_KEY.format(email=email))
        if cached is None or cached != code:
            return DRFResponse(
                data={"detail": "Invalid or expired code."},
                status=HTTP_400_BAD_REQUEST,
            )
        cache.delete(OTP_CACHE_KEY.format(email=email))
        return DRFResponse(
            data={"detail": "OTP verified."},
            status=HTTP_200_OK,
        )


class AddressViewSet(ViewSet):
    """Viewset for handling address-related endpoints."""

    @action(
        methods=("get",),
        detail=False,
        url_path="list",
    )
    def list_addresses(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        serializer = AddressSerializer(
            Address.objects.filter(user=request.user),
            many=True,
        )
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @action(
        methods=("post",),
        detail=False,
        url_path="create",
    )
    def create_address(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        serializer = AddressSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED,
        )

    @action(
        methods=("patch",),
        detail=True,
        url_path="update",
    )
    def update_address(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        address = Address.objects.filter(
            pk=pk,
            user=request.user,
        ).first()
        if not address:
            return DRFResponse(
                {"datail": "Not found"},
                status=HTTP_404_NOT_FOUND,
            )
        serializer = AddressSerializer(
            address,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @action(
        methods=("delete",),
        detail=True,
        url_path="delete",
    )
    def delete_address(
        self,
        request: DRFRequest,
        pk=None,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        address = Address.objects.filter(
            pk=pk,
            user=request.user,
        ).first()
        if not address:
            return DRFResponse(
                {"datail": "Not found"},
                status=HTTP_404_NOT_FOUND,
            )
        address.delete()

        return DRFResponse(
            {"detail": "Deleted"},
            status=HTTP_200_OK,
        )
