"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from testWebSocket import consumers


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # We will add WebSocket routing here soon
    "websocket": URLRouter([
        path("ws/testWebSocket/", consumers.TestConsumer.as_asgi()),
    ]),
})
