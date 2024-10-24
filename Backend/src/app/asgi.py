import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Make sure Django is initialized before importing your chat routing
django.setup()

import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handle traditional HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})