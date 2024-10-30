from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async
from django.db import close_old_connections
import logging

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes JWT from the query string and authenticates the user. <url>?token=<token>
    """
    
    async def __call__(self, scope, receive, send):
        # Extract token from the query string
        query_string = scope['query_string'].decode()
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[1]

        logging.info(f"Token: {token}")
        # If token exists, try to authenticate the user
        if token:
            try:
                # Decode token using rest_framework_simplejwt
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                logging.info(f"Token decoded, user_id: {user_id}")

                # Use Django's auth system to get the user
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = await sync_to_async(User.objects.get)(id=user_id)
                scope['user'] = user
                logging.info(f"User authenticated: {user}")

            except Exception as e:
                print(f"JWT Authentication failed: {e}")
                scope['user'] = AnonymousUser()

        else:
            # If no token is provided, mark the user as AnonymousUser
            # TODO: Probably should return error instead of marking as AnonymousUser
            logging.info("No token provided")
            scope['user'] = AnonymousUser()

        # Close old DB connections to avoid Django DB connection issues
        close_old_connections()

        return await super().__call__(scope, receive, send)
