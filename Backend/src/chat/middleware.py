from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from django.conf import settings
import logging
from core.authentication import CookieJWTAuthentication
from django.core.exceptions import PermissionDenied

class SocketAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that authenticates the user using JWT cookies
    """

    async def __call__(self, scope, receive, send):
        # Verify if using secure connection in production
        if scope.get('scheme') != 'wss':
            logging.error("Rejecting non-WSS connection")
            raise PermissionDenied("WSS required")

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
                raise PermissionDenied("Authentication required")

            return await super().__call__(scope, receive, send)

        except Exception as e:
            logging.error(f"WebSocket authentication failed: {str(e)}")
            scope['user'] = AnonymousUser()
            raise PermissionDenied("Authentication required")
