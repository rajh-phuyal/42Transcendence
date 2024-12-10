from django.urls import path

from tournament.views import (
    CreateTournamentView
)

urlpatterns = [
    path('create/', CreateTournamentView.as_view(), name='create_tournament')
    path('delete/<int:id>/', DeleteTournamentView.as_view(), name='delete_tournament')  # Only admin can do so if not stared
    path('join/<int:id>/', JoinTournamentView.as_view(), name='join_tournament')        # Invited user can join if not started; Public tournament anyone can join
    path('leave/<int:id>/', LeaveTournamentView.as_view(), name='leave_tournament')     # User can leave if not started, this needs to check if to less users are there and then cancel whole tournament
    path('start/<int:id>/', StartTournamentView.as_view(), name='start_tournament')     # Only admin can do so if not started and all users are online
    path('lobby/<int:id>/', TournamentLobbyView.as_view(), name='tournament_lobby')     # Show all users in the tournament and their status
]