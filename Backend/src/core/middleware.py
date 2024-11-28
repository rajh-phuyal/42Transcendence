from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
import logging
from core.cookies import CookieJWTAuthentication
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException


class FailedWebSocketAuthentication(BarelyAnException):
    status_code = 403
    default_detail = _("Failed to authenticate user via WebSocket")
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

            # Parse cookies
            cookies = {}
            if cookie_header:
                for cookie in cookie_header.split(';'):
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        cookies[name.strip()] = value.strip()

            # Create mock request for authentication
            request = type('MockRequest', (), {'COOKIES': cookies})()

            # Authenticate
            auth = CookieJWTAuthentication()
            user_auth = await sync_to_async(auth.authenticate)(request)

            if user_auth:
                user, _ = user_auth
                scope['user'] = user
            else:
                scope['user'] = AnonymousUser()
                raise FailedWebSocketAuthentication(_("Authentication required"))

            return await super().__call__(scope, receive, send)

        except Exception as e:
            logging.error(f"WebSocket authentication failed: {str(e)}")
            scope['user'] = AnonymousUser()
            raise FailedWebSocketAuthentication(_("Authentication required"))
