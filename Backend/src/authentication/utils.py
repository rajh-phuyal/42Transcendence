from django.conf import settings
from datetime import datetime
from django.http import HttpResponse
import logging

def set_jwt_cookies(response: HttpResponse, access_token: str, refresh_token: str = None) -> None:
    """Set JWT tokens as HttpOnly cookies"""

    logging.info(f"Setting access token cookie: {access_token[:10]}...")

    response.set_cookie(
        settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_NAME'],
        access_token,
        expires=datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_HTTPONLY'],
        samesite=settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_PATH']
    )

    if refresh_token:
        logging.info(f"Setting refresh token cookie: {refresh_token[:10]}...")
        response.set_cookie(
            settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_NAME'],
            refresh_token,
            expires=datetime.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_HTTPONLY'],
            samesite=settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_SAMESITE'],
            path=settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_PATH']
        )

    return response

def unset_jwt_cookies(response: HttpResponse) -> None:
    """Remove JWT cookies"""
    response.delete_cookie(
        settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_NAME'],
        path=settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_PATH']
    )
    response.delete_cookie(
        settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_NAME'],
        path=settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_PATH']
    )