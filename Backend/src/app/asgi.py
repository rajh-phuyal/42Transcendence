import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from services import websocket_routing
from core.middleware import WebSocketAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        WebSocketAuthMiddleware(
            URLRouter(
                websocket_routing.websocket_urlpatterns
            )
        )
    ),
})