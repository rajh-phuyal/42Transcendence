from django.urls import path

from game.views import (
    CreateGameView, DeleteGameView
)

urlpatterns = [
     path('create/', CreateGameView.as_view(), name='create_game')
     path('delete/<int:id>/', DeleteGameView.as_view(), name='delete_game')
]