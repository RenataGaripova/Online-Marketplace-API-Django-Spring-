# Python modules
from typing import Callable, Any, Optional

# Django modules
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.utils import translation

# DRF modules
from rest_framework.response import Response as DRFResponse
from rest_framework.request import Request as DRFRequest
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

# Project modules
from settings.base import ENGLISH_LANGUAGE_CODE
from apps.users.models import CustomUser


class CustomLocaleMiddleware:
    """Defines a preferred language for each request."""

    def __init__(
        self, get_response: Callable[[WSGIRequest], DRFResponse]
    ) -> None:
        self.get_response = get_response

    def __call__(
        self,
        request: WSGIRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ):
        """Processes the request to set the language."""
        lang: str = self._determine_language(request=request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response: DRFResponse = self.get_response(request)
        response.headers.setdefault("Content-Language", lang)
        translation.deactivate()
        return response

    def _obtain_user_id_from_jwt(self, request: WSGIRequest) -> Optional[int]:
        """Obtains user id from a request (if user is authenticated)."""

        auth_header: Optional[str] = request.headers.get("Authorization", "")
        if not auth_header.startswith("JWT"):
            return None

        access_token: str = auth_header.strip().split(" ")[1]
        try:
            payload: dict[str, Any] = AccessToken(access_token)
            return payload.get("user_id")
        except TokenError:
            return None

    def _normalize(self, lang: str) -> str:
        """Normalizes a language code."""

        lang = lang.lower()
        return (
            lang
            if lang in CustomUser.PREFFERED_LANGUAGES
            else ENGLISH_LANGUAGE_CODE
        )

    def _determine_language(
        self,
        request: DRFRequest,
    ) -> str:
        """Determines the prioritized language"""

        user_id: Optional[int] = self._obtain_user_id_from_jwt(request=request)
        if user_id is None:
            header_lang: Optional[str] = request.headers.get("App-Language")
            return (
                self._normalize(header_lang)
                if header_lang
                else ENGLISH_LANGUAGE_CODE
            )

        cache_key: str = f"user_lang:{user_id}"
        cached_lang: Optional[str] = cache.get(cache_key)
        if cached_lang is not None:
            return cached_lang

        user: CustomUser = CustomUser.objects.filter(id=user_id).first()
        preffered: Optional[str] = user.preffered_language if user else None
        lang: str = (
            self._normalize(preffered) if preffered else ENGLISH_LANGUAGE_CODE
        )
        cache.set(cache_key, lang, timeout=60 * 10)
        return lang
