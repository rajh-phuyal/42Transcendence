"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from chat import routing

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  		# Handles HTTP requests
    "websocket": AuthMiddlewareStack(  		# Handles WebSocket connections
        URLRouter(
            routing.websocket_urlpatterns 	# WebSocket routes defined in chat/routing.py
        )
    ),
})
