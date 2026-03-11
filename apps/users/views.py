from typing import Any


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

from .models import CustomUser, Address
from .serializers import (
    BaseUserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    AddressSerializer,
)
from apps.abstracts.serializers import (
    RefreshSerializer,
    ErrorDetailSerializer,
    ResponseUserRegistrationSerializer,
)


class CustomUserViewSet(ViewSet):
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
        serializer: UserRegistrationSerializer = UserRegistrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        user: CustomUser = serializer.save()

        # Generate JWT tokens
        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token: AccessToken = refresh_token.access_token

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
        detail=False,
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
