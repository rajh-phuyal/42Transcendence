# Django
from django.utils.translation import gettext as _
# Channels
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
# Tournament
from tournament.models import Tournament, TournamentMember
# Chat
from chat.message_utils import create_and_send_overloards_pm

def send_tournament_invites_via_pm(tournament_id):
    # Get all users that are invited to the tournament
    tournament_admin = TournamentMember.objects.get(tournament_id=tournament_id, is_admin=True)
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id).exclude(is_admin=True)
    tournament = Tournament.objects.get(id=tournament_id)

    for member in tournament_members:
        create_and_send_overloards_pm(
            tournament_admin.user,
            member.user,
            f"**TI,{tournament_admin.user.id},{member.user.id},#T#{tournament.name}#{tournament.id}#**")
