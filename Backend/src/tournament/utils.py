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

def parse_bool(string):
    logging.info(f"parse_bool: {string}")
    if string == "true" or string == "True":
        return True
    return False

def validate_tournament_creation(name, local_tournament, public_tournament, map_number, powerups):
    if name is None or not isinstance(name, str):
        raise BarelyAnException(_("Can't create a tournament without a name"))

    local_tournament_bool = parse_bool(local_tournament)
    public_tournament_bool = parse_bool(public_tournament)
    powerups_bool = parse_bool(powerups)

    if map_number is None or not isinstance(map_number, int):
        raise BarelyAnException(_("Can't create a tournament without specifying a map number"))
    if map_number not in [1, 2, 3, 4]:
        raise BarelyAnException(_("Invalid map number"))

    return local_tournament_bool, public_tournament_bool, powerups_bool
def validate_tournament_users(creator_id, opponent_ids, local_tournament, public_tournament):
    # Get creator of the tournament
    try:
        creator = User.objects.get(id=creator_id)
    except User.DoesNotExist:
        raise BarelyAnException(_("Creator not found"))

    # Check if the creator is already in a tournament which is not finished
    if TournamentMember.objects.filter(
        user=creator,
        tournament__state__in=[TournamentState.SETUP, TournamentState.ONGOING]
    ).exists():
        raise BarelyAnException(_("You can't create a new tournament while you are in another one"))

    # Prepare the list of tournament users (creator is always included)
    tournament_user_objects = []
    tournament_user_objects.append(creator)

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
            logging.error("TODO: Playing against AI is not supported yet")
        if is_blocking(creator, opponent):
            raise BlockingException(_("You can't invite a user whom you have blocked: {opponent.username}").format(opponent=opponent))
        if is_blocked(creator, opponent):
            raise BlockingException(_("You can't invite a user who has blocked you: {opponent.username}").format(opponent=opponent))
        if not are_friends(creator, opponent):
            raise BarelyAnException(_("You can only invite your friends to a tournament: {opponent.username}").format(opponent=opponent))
        tournament_user_objects.append(opponent)
    return tournament_user_objects

def create_tournament(creator_id, name, local_tournament, public_tournament, map_number, powerups_string, opponent_ids=None):
        # Validate args
        local, public, powerups = validate_tournament_creation(name, local_tournament, public_tournament, map_number, powerups_string)
        tournament_user_objects = validate_tournament_users(creator_id, opponent_ids, local, public)

        # Create the tournament and the tournament members in a single transaction
        with transaction.atomic():
            tournament = Tournament.objects.create(
                name=name,
                local_tournament=local,
                public_tournament=public,
                map_number=map_number,
                powerups=powerups,
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

def get_tournament_and_member(user, tournament_id, need_admin=False):
    # Get the tournament
    tournament = Tournament.objects.get(id=tournament_id).select_for_update()
    try:
        tournament_member = TournamentMember.objects.get(user_id=user.id, tournament_id=tournament.id).select_for_update()
    except TournamentMember.DoesNotExist:
        raise BarelyAnException(_("You are not a member of the tournament"))
    # Check if the user is the admin of the tournament
    if need_admin and not tournament_member.is_admin:
        raise BarelyAnException(_("You are not the admin of the tournament"))
    return tournament, tournament_member

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
        if tournament_member:
            # Check if already accepted
            if tournament_member.accepted:
                raise BarelyAnException(_("You have already accepted this tournament invitation"))
            # Accept the invitation
            if tournament.state != TournamentState.SETUP:
                raise BarelyAnException(_("Tournament has already started or ended"))
            else:
                tournament_member.accepted = True
                tournament_member.save()
                # TODO: send websocket update message to update the lobby

        # In case we don't have an entry:
        else:
            if not tournament.public_tournament:
                raise BarelyAnException(_("You are not invited to this tournament"), status_code=status.HTTP_403_FORBIDDEN)
            else:
                if tournament.state != TournamentState.SETUP:
                    raise BarelyAnException(_("Tournament has already started or ended"))
                else:
                    tournament_member = TournamentMember.objects.create(
                        user=user,
                        tournament=tournament,
                        tournament_alias=user.username,
                        accepted=True
                    )
                    tournament_member.save()
                    # TODO: send websocket update message to update the lobby

