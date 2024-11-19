from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from django.db import close_old_connections
import logging
from django.conf import settings

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes JWT from the query string and authenticates the user. <url>?token=<token>
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
        access_token = cookies.get(settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_NAME'])

        if access_token:
            try:
                # Decode token
                access_token = AccessToken(access_token)
                user_id = access_token['user_id']
                logging.info(f"User ID: {user_id}")

                # Get user
                User = get_user_model()
                user = await sync_to_async(User.objects.get)(id=user_id)
                scope['user'] = user
                logging.info(f"User: {user}")

            except Exception as e:
                logging.info(f"Anonymous user")
                raise e

        else:
            logging.info(f"No access token found")
            raise Exception("No access token found")

        close_old_connections()

        return await super().__call__(scope, receive, send)
