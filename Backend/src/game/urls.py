from django.urls import path

from game.views import (
    CreateGameView
)

urlpatterns = [
     path('create/', CreateGameView.as_view(), name='create_game')
]