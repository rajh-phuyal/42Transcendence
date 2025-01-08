from django.urls import path
from .websocket_consumers import MainConsumer, GameConsumer

websocket_urlpatterns = [
    path('ws/app/main/', MainConsumer.as_asgi()),
    path('ws/app/game/<int:game_id>/', GameConsumer.as_asgi())
]
