from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
import logging
from core.cookies import CookieJWTAuthentication
from django.utils.translation import gettext as _gt
from core.exceptions import BarelyAnException


class FailedWebSocketAuthentication(BarelyAnException):
    status_code = 403
    default_detail = _gt("Failed to authenticate user via WebSocket")
    def __init__(self, detail, status_code=403):
        super().__init__(detail)
        self.detail = detail
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
            logging.info(f"WebSocket connection attempt with cookies: {cookie_header}")

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
