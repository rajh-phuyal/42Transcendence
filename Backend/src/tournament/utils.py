from tournament.models import Tournament, TournamentMember, TournamentState
from core.exceptions import BarelyAnException
from user.exceptions import RelationshipException, BlockingException
from user.models import User
from game.models import Game, GameMember
from django.db import transaction
from django.utils.translation import gettext as _
from user.constants import USER_ID_AI
from user.utils_relationship import are_friends, is_blocking, is_blocked
import logging
from rest_framework import status
from tournament.utils_ws import send_tournament_ws_msg, delete_tournament_channel
from tournament.constants import MAX_PLAYERS_FOR_TOURNAMENT
from .serializer import TournamentMemberSerializer

def validate_tournament_creation(name, map_number):
    if name is None or not isinstance(name, str):
        raise BarelyAnException(_("Can't create a tournament without a name"))
    if map_number is None or not isinstance(map_number, int):
        raise BarelyAnException(_("Can't create a tournament without specifying a map number"))
    if map_number not in [1, 2, 3, 4]:
        raise BarelyAnException(_("Invalid map number"))

def validate_tournament_users(creator_id, opponent_ids, local_tournament, public_tournament):
    # Get creator of the tournament
    try:
        creator = User.objects.get(id=creator_id)
    except User.DoesNotExist:
        raise BarelyAnException(_("Creator not found"))

    # Check if the creator is already in a tournament which is not finished
    if TournamentMember.objects.filter(
        user=creator,
        tournament__state__in=[TournamentState.SETUP, TournamentState.ONGOING],
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

def delete_tournament(user, tournament_id):
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

        # Check if the user is the admin of the tournament
        if not tournament_member.is_admin:
            raise BarelyAnException(_("You are not the admin of the tournament"), status_code=status.HTTP_403_FORBIDDEN)
        # Check if the tournament has already started
        if not tournament.state == TournamentState.SETUP:
            raise BarelyAnException(_("Tournament can only be deleted if it is in setup state"))
        # Delete the tournament
        tournament_members.delete()
        tournament.delete()
    # inform users and delete the channel
    send_tournament_ws_msg(
        tournament_id,
        "tournamentState",
        "tournament_state",
        _("The admin has deleted the tournament!"),
        **{"state": "delete"}
    )
    delete_tournament_channel(tournament_id)

def join_tournament(user, tournament_id):
    with transaction.atomic():
        tournament = Tournament.objects.select_for_update().get(id=tournament_id)
        # Check if already a member
        tournament_member = None
        try:
            tournament_member = TournamentMember.objects.select_for_update().get(user_id=user.id, tournament_id=tournament_id)
        except TournamentMember.DoesNotExist:
            ...
            # Ignore the error

        # In case we already have an entry:
        if (tournament_member and tournament_member.accepted):
            raise BarelyAnException(_("You have already accepted this tournament invitation"))
            # Accept the invitation
        if (tournament_member and tournament.state != TournamentState.SETUP):
                raise BarelyAnException(_("Tournament has already started or ended"))
        if tournament_member:
            tournament_member.accepted = True
            tournament_member.save()
            data = TournamentMemberSerializer(tournament_member).data
            # Send message via websocket
            send_tournament_ws_msg(
                tournament_id,
                "tournamentSubscription",
                "tournament_subscription",
                _("{username} accepted the tournament invitation").format(username=user.username),
                **data
            )
            return

        # In case we don't have an entry:
        if not tournament.public_tournament:
            raise BarelyAnException(_("You are not invited to this tournament"), status_code=status.HTTP_403_FORBIDDEN)
        if tournament.state != TournamentState.SETUP:
            raise BarelyAnException(_("Tournament has already started or ended"))
        members_count = TournamentMember.objects.filter(tournament_id=tournament_id).count()
        if members_count >= MAX_PLAYERS_FOR_TOURNAMENT:
            raise BarelyAnException(_("Tournament is full"))
        tournament_member = TournamentMember.objects.create(
            user=user,
            tournament=tournament,
            tournament_alias=user.username,
            accepted=True
        )
        tournament_member.save()
    # Send message via websocket
    send_tournament_ws_msg(
        tournament_id,
        "tournamentSubscription",
        "tournament_subscription",
        _("{username} joined the tournament").format(username=user.username),
        **{
            "userId": user.id,
            "state": "join"
        }
    )

def leave_tournament(user, tournament_id):
    with transaction.atomic():
        tournament = Tournament.objects.select_for_update().get(id=tournament_id)
        # Check if already a member
        tournament_member = None
        try:
            tournament_member = TournamentMember.objects.select_for_update().get(user_id=user.id, tournament_id=tournament_id)
        except TournamentMember.DoesNotExist:
            raise BarelyAnException(_("You are not a member of the tournament"), status_code=status.HTTP_403_FORBIDDEN)

        if tournament.state != TournamentState.SETUP:
            raise BarelyAnException(_("Tournament can only be left if it is in setup state"))
        if tournament_member.is_admin:
            raise BarelyAnException(_("Admin can't leave the tournament. Please delete the tournament instead"))
        # Delete the tournament member
        tournament_member.delete()
        # TODO: check if there are enough players left and cancel the tournament if not (only for private tournaments)
    # Send websocket update message to admin to update the lobby
    if tournament_member.accepted:
        message=_("User {username} left the tournament").format(username=user.username)
    else:
        message=_("User {username} declined the tournament invitation").format(username=user.username)
        data = TournamentMemberSerializer(tournament_member).data
    send_tournament_ws_msg(
        tournament_id,
        "tournamentSubscription",
        "tournament_subscription",
        message,
        **{
            "userId" : user.id,
            "state": "leave"
        }
    )
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
            raise BarelyAnException(_("You are not the admin of the tournament"), status_code=status.HTTP_403_FORBIDDEN)
        if not tournament.state == TournamentState.SETUP:
            raise BarelyAnException(_("Tournament can only be started if it is in setup state"))
        # Check if at least 3 members are there
        tournament_members_count = tournament_members.filter(accepted=True).count()
        if tournament_members_count < 3:
            raise BarelyAnException(_("You need at least 3 members to start the tournament"))
        # Check if all members are online
        if not all([tournament_members.user.get_online_status() for tournament_members in tournament_members]):
            raise BarelyAnException(_("All members must be online to start the tournament"))
        # Start the tournament
        tournament.state = 'ongoing'
        tournament.save()
        # Remove all persons who have not accepted the invitation
        tournament_members.filter(accepted=False).delete()
        tournament_members_after_start = TournamentMember.objects.filter(tournament_id=tournament_id)
    # Send websocket update message to all members to start the game
    send_tournament_ws_msg(
        tournament_id,
        "tournamentState",
        "tournament_state",
        _("{username} started the tournament '{name}'! Go to lobby to not miss a game!").format(username=user.username, name=tournament.name),
        **{"state": "start"}
    )
    # create the games
    create_initial_games(tournament, tournament_members_after_start)

def finish_tournament(tournament):
    # THE TOURNAMENT IS OVER!!!
    # The rank by now is already set due to:
    # game_utils.finish_game() -> tournament_manager.update_tournament_ranks()
    # so only:
    # - set the tournament state to finished
    with transaction.atomic():
        tournament.state = TournamentState.FINISHED
        tournament.save()
    # - send the websocket message
    send_tournament_ws_msg(
        tournament.id,
        "tournamentState",
        "tournament_state",
        _("The tournament has finished!"),
        **{"state": "finished"}
    )
    # - closse the channel
    delete_tournament_channel(tournament.id)
    logging.info(f"Tournament {tournament.id} has finished!")