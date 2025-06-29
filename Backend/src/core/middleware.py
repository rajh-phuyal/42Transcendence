# Basics
import logging
# Django
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from rest_framework import status
# Core
from core.exceptions import BarelyAnException
from core.cookies import CookieJWTAuthentication

class FailedWebSocketAuthentication(BarelyAnException):
    def __init__(self, detail=None, status_code=status.HTTP_403_FORBIDDEN):
        super().__init__(detail)
        self.detail = detail or _("Failed to authenticate user via WebSocket")
        self.status_code = status_code

class WebSocketAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that authenticates the user using JWT cookies
    """

    async def __call__(self, scope, receive, send):
        # Extract and validate cookies
        try:
            headers = dict(scope['headers'])
            cookie_header = headers.get(b'cookie', b'').decode()
            # Parse cookies
            cookies = {}
            if cookie_header:
                for cookie in cookie_header.split(';'):
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        cookies[name.strip()] = value.strip()
            else:
                logging.error("No cookies found in WebSocket request")
                scope['user'] = AnonymousUser()
                return await super().__call__(scope, receive, send)

            # Create mock request for authentication
            request = type('MockRequest', (), {'COOKIES': cookies})()

            # Authenticate
            auth = CookieJWTAuthentication()
            try:
                user_auth = await sync_to_async(auth.authenticate)(request)
                if user_auth:
                    user, _ = user_auth
                    scope['user'] = user
                    logging.info(f"WebSocket authenticated for user: {user.username}")
                else:
                    logging.error("WebSocket authentication failed: No user returned from authenticate")
                    scope['user'] = AnonymousUser()
            except Exception as auth_error:
                logging.error(f"WebSocket authentication error: {str(auth_error)}")
                scope['user'] = AnonymousUser()

            return await super().__call__(scope, receive, send)

        except Exception as e:
            logging.error(f"WebSocket middleware error: {str(e)}")
            scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)
