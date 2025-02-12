from django.urls import path
from .websocket_consumers_game import GameConsumer
from .websocket_consumers_main import MainConsumer

websocket_urlpatterns = [
    path('ws/app/main/', MainConsumer.as_asgi()),
    path('ws/app/game/<int:game_id>/', GameConsumer.as_asgi())
    # TODO: REMOVE WHEN FINISHED #284
    # CHECK IF THE CONNECTION IS ALLOWED aka game exists full stack!!
]
