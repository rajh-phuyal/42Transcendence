from django.urls import path

from game.views import (
    CreateGameView, DeleteGameView, LobbyView, PlayAgainView, GetGameView, HistoryView
)

urlpatterns = [
    path('create/', CreateGameView.as_view(), name='create_game'),
    path('get-game/<int:userid>/', GetGameView.as_view(), name='get_game'),
    path('delete/<int:id>/', DeleteGameView.as_view(), name='delete_game'),
    path('lobby/<int:id>/', LobbyView.as_view(), name='lobby'),
    path('history/<int:userid>/', HistoryView.as_view(), name='history'),
    path('play-again/<int:id>/', PlayAgainView.as_view(), name='play_again')
]
