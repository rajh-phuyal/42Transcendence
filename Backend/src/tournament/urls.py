from django.urls import path

from tournament.views import (
    EnrolmentView,
    HistoryView,
    ActiveView,
    CreateTournamentView,
    DeleteTournamentView,
    JoinTournamentView,
    LeaveTournamentView,
    StartTournamentView,
    TournamentLobbyView
)

urlpatterns = [
    path('enrolment/', EnrolmentView.as_view(), name='enrolment'),
    path('history/', HistoryView.as_view(), name='history'),
    path('active/', ActiveView.as_view(), name='active'),
    path('create/', CreateTournamentView.as_view(), name='create_tournament'),
    path('delete/<int:id>/', DeleteTournamentView.as_view(), name='delete_tournament'),
    path('join/<int:id>/', JoinTournamentView.as_view(), name='join_tournament'),
    path('leave/<int:id>/', LeaveTournamentView.as_view(), name='leave_tournament'),
    path('start/<int:id>/', StartTournamentView.as_view(), name='start_tournament'),
    path('lobby/<int:id>/', TournamentLobbyView.as_view(), name='tournament_lobby'),
]