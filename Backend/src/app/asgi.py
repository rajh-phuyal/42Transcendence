import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Make sure Django is initialized before importing your chat routing
django.setup()

logging.warning(f'DJANGO_SETTINGS_MODULE is set to: {os.environ["DJANGO_SETTINGS_MODULE"]}')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handle traditional HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            __import__('chat.routing').routing.websocket_urlpatterns  # Import WebSocket routes dynamically
        )
    ),
})