import logging
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.translation import gettext as _
from core.exceptions import NotAuthenticated


JAR = settings.SIMPLE_JWT_COOKIE


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            # Get the token from cookie
            token = request.COOKIES.get('access_token')

            if not token:
                raise NotAuthenticated(_("Authentication credentials were not provided."), status_code=401)

            validated_token = self.get_validated_token(token)
            user = self.get_user(validated_token)
            return user, validated_token

        except TokenError as e:
            raise NotAuthenticated(_("Invalid or expired token."), status_code=401)
        except InvalidToken as e:
            raise NotAuthenticated(_("Invalid or expired token."), status_code=401)
        except Exception as e:
            raise NotAuthenticated(_("Authentication failed."), status_code=401)


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
