# Basics
import logging
from rest_framework import status
# Django
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import transaction
# Core
from core.exceptions import BarelyAnException
# Services
from services.send_ws_msg import send_ws_tournament_pm, send_ws_tournament_info_msg, send_ws_tournament_member_msg
from services.channel_groups import delete_tournament_group
# User
from user.constants import USER_ID_AI
from user.models import User
from user.exceptions import BlockingException
from user.utils import get_user_by_id
from user.utils_relationship import are_friends, is_blocking, is_blocked
# Game
from game.models import Game
# Tournament
from tournament.constants import MAX_PLAYERS_FOR_TOURNAMENT
from tournament.models import Tournament, TournamentMember
from tournament.serializer import TournamentGameSerializer, TournamentMemberSerializer
# Chat
from chat.message_utils import create_and_send_overloards_pm

def validate_tournament_creation(name, map_number):
    if name is None or not isinstance(name, str):
        raise BarelyAnException(_("Can't create a tournament without a name"))
    if map_number is None or not isinstance(map_number, int):
        raise BarelyAnException(_("Can't create a tournament without specifying a map number"))
    if map_number not in [1, 2, 3, 4]:
        raise BarelyAnException(_("Invalid map number"))

def validate_tournament_users(creator_id, opponent_ids, local_tournament, public_tournament):
    # Get creator of the tournament
    creator = get_user_by_id(creator_id)

    # Check if the creator is already in a tournament which is not finished
    if TournamentMember.objects.filter(
        user=creator,
        tournament__state__in=[Tournament.TournamentState.SETUP, Tournament.TournamentState.ONGOING],
        accepted=True
    ).exists():
        raise BarelyAnException(_("You can't create a new tournament while you are in another one"))

    # Prepare the list of tournament users (creator is always included)
    tournament_user_objects = []
    tournament_user_objects.append(creator)

    if not opponent_ids:
        opponent_ids = None

    # Validate tournament params for edge cases
    if local_tournament and public_tournament:
        raise BarelyAnException(_("Tournament can't be both local and public"))
    if local_tournament and opponent_ids is None:
        raise BarelyAnException(_("Local tournaments require opponent ids"))
    if public_tournament and opponent_ids is not None:
        raise BarelyAnException(_("Public tournaments can't have opponent ids"))
    if not local_tournament and not public_tournament and opponent_ids is None:
        raise BarelyAnException(_("You must invite opponents to a private tournament"))
    if opponent_ids is None:
        return tournament_user_objects
    if not isinstance(opponent_ids, list):
        raise BarelyAnException(_("Opponent ids must be a list"))
    if len(opponent_ids) < 2:
        raise BarelyAnException(_("You must invite at least two opponents to a tournament"))

    # Validate max number of players
    if len(opponent_ids) + 1 > MAX_PLAYERS_FOR_TOURNAMENT:
        raise BarelyAnException(_("You can't invite more than {max_players} players to a tournament").format(max_players=MAX_PLAYERS_FOR_TOURNAMENT))

    # Validate all opponent ids
    for opponent_id in opponent_ids:
        if not isinstance(opponent_id, int):
            raise BarelyAnException(_("Opponent ids must be integers"))
        try:
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
            raise BarelyAnException(_("Opponent not found: {opponent_id}").format(opponent_id=opponent_id))
        if creator_id == opponent_id:
            raise BarelyAnException(_("You can't invite yourself to a tournament"))
        if opponent.id == USER_ID_AI:
            logging.error("TODO: Playing against AI is not supported yet! issue #216")
        if is_blocking(creator, opponent):
            raise BlockingException(_("You can't invite a user whom you have blocked: {opponent.username}").format(opponent=opponent))
        if is_blocked(creator, opponent):
            raise BlockingException(_("You can't invite a user who has blocked you: {opponent.username}").format(opponent=opponent))
        if not are_friends(creator, opponent):
            raise BarelyAnException(_("You can only invite your friends to a tournament: {opponent.username}").format(opponent=opponent))
        tournament_user_objects.append(opponent)
    return tournament_user_objects

def create_tournament(creator_id, name, local_tournament, public_tournament, map_number, powerups, opponent_ids=None):
    # Validate args
    validate_tournament_creation(name, map_number)
    tournament_user_objects = validate_tournament_users(creator_id, opponent_ids, local_tournament, public_tournament)

    # Create the tournament and the tournament members in a single transaction
    with transaction.atomic():
        tournament = Tournament.objects.create(
            name=name,
            local_tournament=local_tournament,
            public_tournament=public_tournament,
            map_number=map_number,
            powerups=powerups
        )
        tournament.save()

        for user in tournament_user_objects:
            if user.id == creator_id:
                tournament_member = TournamentMember.objects.create(
                    user=user,
                    tournament=tournament,
                    tournament_alias=user.username,
                    is_admin=True,
                    accepted=True
                )
            else:
                tournament_member = TournamentMember.objects.create(
                    user=user,
                    tournament=tournament,
                    tournament_alias=user.username,
                )
            tournament_member.save()
    return tournament

def delete_tournament(user, tournament_id, to_less_players=False):
    """
    This function is called by the endpoint to delete a tournament and by the
    leave_tournament function to delete a tournament if there are not enough
    players left. The to less players flag is set to True in the latter case.
    """
    tournament = Tournament.objects.get(id=tournament_id)
    if not to_less_players:
        try:
            tournament_member = TournamentMember.objects.get(user_id=user.id, tournament_id=tournament_id)
        except TournamentMember.DoesNotExist:
            raise BarelyAnException(_("You are not a member of the tournament"), status_code=status.HTTP_403_FORBIDDEN)
        if not tournament_member.is_admin:
            raise BarelyAnException(_("You are not the admin of the tournament"), status_code=status.HTTP_403_FORBIDDEN)
        if not tournament.state == Tournament.TournamentState.SETUP:
            raise BarelyAnException(_("Tournament can only be deleted if it is in setup state"))

    # First inform the users...
    send_ws_tournament_info_msg(tournament, deleted=True)
    # ... also send as PM ...
    if to_less_players:
        send_ws_tournament_pm(tournament_id, f"**TDO,{tournament.as_clickable()}**")
    else:
        send_ws_tournament_pm(tournament_id, f"**TDA,{tournament.as_clickable()}**")
    # ... then delete everything
    with transaction.atomic():
        tournament = Tournament.objects.select_for_update().get(id=tournament_id)
        try:
            tournament_members = TournamentMember.objects.select_for_update().filter(tournament_id=tournament_id)
            tournament_members.delete()
        except TournamentMember.DoesNotExist:
            logging.info("No members found for the tournament - this is strange :D")
        tournament.delete()
    delete_tournament_group(tournament_id)

def join_tournament(user, tournament_id):
    """
    There are two similar but different ways to join a tournament:
    Private Tournament: u need to be invited -> set accepted to True
    Public Tournament: u can join -> create a new entry
    """

    tournament = Tournament.objects.get(id=tournament_id)
    # Check if already a member
    tournament_member = None
    try:
        tournament_member = TournamentMember.objects.get(user_id=user.id, tournament_id=tournament_id)
        if tournament_member.accepted:
            raise BarelyAnException(_("You are already a member of the tournament"))
    except TournamentMember.DoesNotExist:
        ...
        # Ignore the error for now

    # Tournament state check
    if tournament.state == Tournament.TournamentState.ONGOING:
        raise BarelyAnException(_("Tournament has already started - too late to join"))
    if tournament.state == Tournament.TournamentState.FINISHED:
        raise BarelyAnException(_("Tournament has already ended - too late to join"))

    if tournament.public_tournament:
        # Check if tournament is full
        members_count = TournamentMember.objects.filter(tournament_id=tournament_id).count()
        if members_count + 1 > MAX_PLAYERS_FOR_TOURNAMENT:
            raise BarelyAnException(_("Tournament is full"))
        # Create an entry
        tournament_member = TournamentMember.objects.create(
            user=user,
            tournament=tournament,
            tournament_alias=user.username,
            accepted=True
        )
    else:
        # Need to be invited
        if not tournament_member:
            raise BarelyAnException(_("You are not invited to this tournament"), status_code=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            tournament_member = TournamentMember.objects.select_for_update().get(user_id=user.id, tournament_id=tournament_id)
            tournament_member.accepted = True
            tournament_member.save()

    # Send the member update to tournament channel group
    send_ws_tournament_member_msg(tournament_member)
    # Send a PM between admin and new member
    message = f"**TJ,{tournament_member.user.id},{tournament_member.tournament.as_clickable()}**"
    create_and_send_overloards_pm(tournament_member.user, tournament_member.tournament.members.get(is_admin=True).user, message)

def leave_tournament(user, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    # Check if client is part of the tournament
    tournament_member = None
    try:
        tournament_member = TournamentMember.objects.get(user_id=user.id, tournament_id=tournament_id)
    except TournamentMember.DoesNotExist:
        raise BarelyAnException(_("You are not a member of this tournament"), status_code=status.HTTP_403_FORBIDDEN)
    # Tournament state check
    if tournament.state == Tournament.TournamentState.ONGOING:
        raise BarelyAnException(_("Tournament has already started - too late to leave"))
    if tournament.state == Tournament.TournamentState.FINISHED:
        raise BarelyAnException(_("Tournament has already ended - too late to leave"))
    # Admin can't leave (needs to delete the tournament instead)
    if tournament_member.is_admin:
            raise BarelyAnException(_("Admin can't leave the tournament. Please delete the tournament instead"))
    # First inform the users via the group channel ...
    send_ws_tournament_member_msg(tournament_member, leave=True)
    # ... also send a PM to the admin ...
    message = f"**TL,{user.id},{tournament.as_clickable()}**"
    create_and_send_overloards_pm(tournament_member.user, tournament_member.tournament.members.get(is_admin=True).user, message)
    # ... then delete the entry
    with transaction.atomic():
        tournament_member = TournamentMember.objects.select_for_update().get(user_id=user.id, tournament_id=tournament_id)
        tournament_member.delete()

    # Check if there are enough players left and cancel the tournament if not (only for private tournaments)
    if tournament.public_tournament:
        return
    members_left = TournamentMember.objects.filter(tournament_id=tournament_id).count()
    if members_left < 3:
        delete_tournament(user, tournament_id, to_less_players=True)
    return

def start_tournament(user, tournament_id):
    from tournament.tournament_manager import create_initial_games
    with transaction.atomic():
        tournament = Tournament.objects.select_for_update().get(id=tournament_id)
        # Check if already a member
        tournament_member = None
        tournament_members = None
        try:
            tournament_member = TournamentMember.objects.select_for_update().get(user_id=user.id, tournament_id=tournament_id)
            tournament_members = TournamentMember.objects.select_for_update().filter(tournament_id=tournament_id)
        except TournamentMember.DoesNotExist:
            raise BarelyAnException(_("You are not a member of the tournament"), status_code=status.HTTP_403_FORBIDDEN)

        if not tournament_member.is_admin:
            raise BarelyAnException(_("Only the admin can start the tournament!"), status_code=status.HTTP_403_FORBIDDEN)
        if not tournament.state == Tournament.TournamentState.SETUP:
            raise BarelyAnException(_("Tournament can only be started if it is in setup state"))
        # Check if at least 3 members are there
        tournament_members_count = tournament_members.filter(accepted=True).count()
        if tournament_members_count < 3:
            raise BarelyAnException(_("You need at least 3 members to start the tournament"))
        # Check if all members who accepted the invitation are online
        accepted_members = tournament_members.filter(accepted=True)
        not_accepted_members = tournament_members.filter(accepted=False)
        if not all([tournament_members.user.get_online_status() for tournament_members in accepted_members]):
            raise BarelyAnException(_("All members who joined the tournament need to be online to start the tournament"))
        # Start the tournament
        tournament.state = Tournament.TournamentState.ONGOING
        tournament.save()
        # Remove all persons who have not accepted the invitation
        for member in not_accepted_members:
            send_ws_tournament_member_msg(member, leave=True)
            member.delete()
    # Send websocket update message to tournament channel group to update the lobby
    send_ws_tournament_info_msg(tournament)
    # Also send a PM to all members
    message = f"**TS,{tournament.as_clickable()}**"
    send_ws_tournament_pm(tournament_id, message)
    # create the games
    create_initial_games(tournament, accepted_members)

def finish_tournament(tournament):
    # THE TOURNAMENT IS OVER!!!
    # The rank by now is already set due to:
    # game_utils.finish_game() -> tournament_manager.update_tournament_ranks()
    # so only:
    # - set the tournament state to finished
    with transaction.atomic():
        tournament.state = Tournament.TournamentState.FINISHED
        tournament.finish_time = timezone.now()
        tournament.save()
    # - send the websocket message
    send_ws_tournament_info_msg(tournament)
    # - close the channel
    delete_tournament_group(tournament.id)
