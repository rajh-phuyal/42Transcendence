from django.urls import path

from tournament.views import (
    CreateTournamentView
)

urlpatterns = [
     path('create/', CreateTournamentView.as_view(), name='create_tournament')
]