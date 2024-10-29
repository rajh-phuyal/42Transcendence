from django.urls import path
from chat import consumers
# Import additional consumers here as needed (e.g., for `game`, `tournament` apps)

websocket_urlpatterns = [
    path('ws/app/main/', consumers.ChatConsumer.as_asgi()),  # WebSocket URL for chat

    # You can add other app routes here as needed, e.g.,
    # path("ws/game/", GameConsumer.as_asgi()),
    # path("ws/tournament/", TournamentConsumer.as_asgi()),
]
