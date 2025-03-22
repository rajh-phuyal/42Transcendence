from django.urls import path

from tournament.views import (
    EnrolmentView,
    HistoryView,
    ToJoinView,
    CreateTournamentView,
    DeleteTournamentView,
    JoinTournamentView,
    LeaveTournamentView,
    StartTournamentView,
    TournamentLobbyView,
    GoToGameView
)

urlpatterns = [
    path('enrolment/', EnrolmentView.as_view(), name='enrolment'),
    path('history/<int:userid>/', HistoryView.as_view(), name='history'),
    path('to-join/', ToJoinView.as_view(), name='to_join'),
    path('create/', CreateTournamentView.as_view(), name='create_tournament'),
    path('delete/<int:id>/', DeleteTournamentView.as_view(), name='delete_tournament'),
    path('join/<int:id>/', JoinTournamentView.as_view(), name='join_tournament'),
    path('leave/<int:id>/', LeaveTournamentView.as_view(), name='leave_tournament'),
    path('start/<int:id>/', StartTournamentView.as_view(), name='start_tournament'),
    path('lobby/<int:id>/', TournamentLobbyView.as_view(), name='tournament_lobby'),
    path('go-to-game/', GoToGameView.as_view(), name='go_to_game'),
]