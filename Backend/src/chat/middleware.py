from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from django.db import close_old_connections
import logging
from django.conf import settings
from authentication.authentication import CookieJWTAuthentication

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that authenticates the user using JWT cookies
    """

    async def __call__(self, scope, receive, send):
        # Extract token from cookies
        headers = dict(scope['headers'])
        cookie_header = headers.get(b'cookie', b'').decode()

        # Parse cookies
        cookies = {}
        if cookie_header:
            cookies = {
                cookie.split('=')[0].strip(): cookie.split('=')[1].strip()
                for cookie in cookie_header.split(';')
            }

        logging.info(f"Cookies: {cookies}")

        # Create mock request object for the authentication class
        class MockRequest:
            def __init__(self, cookies):
                self.COOKIES = cookies

        request = MockRequest(cookies)

        try:
            auth = CookieJWTAuthentication()
            user_auth = await sync_to_async(auth.authenticate)(request)

            if user_auth:
                user, _ = user_auth
                logging.info(f"User ID: {user.id}")
                logging.info(f"User: {user}")
                scope['user'] = user
            else:
                logging.info("No valid authentication found")
                scope['user'] = AnonymousUser()
                raise Exception("No valid authentication")

        except Exception as e:
            logging.info(f"Anonymous user due to: {str(e)}")
            scope['user'] = AnonymousUser()
            raise e

        close_old_connections()

        return await super().__call__(scope, receive, send)
