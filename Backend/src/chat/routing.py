from django.urls import path
from . import consumers

# Below the ws is choosen because django channels will automatically use wss for secure connections
websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),  # WebSocket URL for chat
]
