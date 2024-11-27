from django.conf import settings
from datetime import datetime
from django.http import HttpResponse
import logging

JAR = settings.SIMPLE_JWT_COOKIE

def set_jwt_cookies(response: HttpResponse, access_token: str, refresh_token: str = None) -> HttpResponse:
    """Set JWT tokens as HttpOnly cookies"""

    logging.info(f"Setting access token cookie: {access_token[:30]}...")

    response.set_cookie(
        JAR['ACCESS_COOKIE_NAME'],
        access_token,
        expires=datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=JAR['ACCESS_COOKIE_SECURE'],
        httponly=JAR['ACCESS_COOKIE_HTTPONLY'],
        samesite=JAR['ACCESS_COOKIE_SAMESITE'],
        path=JAR['ACCESS_COOKIE_PATH']
    )

    if refresh_token:
        logging.info(f"Setting refresh token cookie: {refresh_token[:10]}...")
        response.set_cookie(
            JAR['REFRESH_COOKIE_NAME'],
            refresh_token,
            expires=datetime.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=JAR['REFRESH_COOKIE_SECURE'],
            httponly=JAR['REFRESH_COOKIE_HTTPONLY'],
            samesite=JAR['REFRESH_COOKIE_SAMESITE'],
            path=JAR['REFRESH_COOKIE_PATH']
        )

    return response

def unset_jwt_cookies(response: HttpResponse) -> HttpResponse:
    """Remove JWT cookies"""
    response.delete_cookie(
        JAR['ACCESS_COOKIE_NAME'],
        path=JAR['ACCESS_COOKIE_PATH']
    )
    response.delete_cookie(
        JAR['REFRESH_COOKIE_NAME'],
        path=JAR['REFRESH_COOKIE_PATH']
    )

    return response
