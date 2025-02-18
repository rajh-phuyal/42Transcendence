# Basics
import logging
# DJANGO
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _
# CORE
from core.exceptions import BarelyAnException
# USER
from user.constants import USER_ID_AI
from user.models import User
from user.exceptions import RelationshipException, BlockingException
from user.utils_relationship import is_blocking, are_friends
# GAME
from game.constants import MAPNAME_TO_MAPNUMBER
from game.models import Game, GameMember
# TOURNAMENT
from tournament.constants import DEADLINE_FOR_TOURNAMENT_GAME_START
from tournament.tournament_manager import check_tournament_routine, update_tournament_ranks
from services.send_ws_msg import send_ws_tournament_game_msg
from tournament.ranking import update_tournament_member_stats
from user.utils import get_user_by_id
# CHAT
from chat.message_utils import create_and_send_overloards_pm

def map_name_to_number(map_name):
    return MAPNAME_TO_MAPNUMBER.get(map_name.lower(), None)

def create_game(user, opponent_id, map_number, powerups, local_game):
        # Check if opponent exist
        opponent = get_user_by_id(opponent_id)
        # Check if opponent isn't urself, is ur friend and not blocking you
        if user.id == opponent_id:
            raise BarelyAnException(_("You can't play against yourself"))
        if not are_friends(user, opponent):
            raise RelationshipException(_("You can only play against your friends"))
        if is_blocking(opponent, user):
            raise BlockingException(_("Opponent is blocking you"))
        if not map_number in [1, 2, 3, 4]:
            raise BarelyAnException(_("Invalid value for key 'mapNumber' value (must be 1, 2, 3 or 4)"))
        if not opponent_id:
            raise BarelyAnException(_("Missing key 'opponentId'"))
        # Check if opponent is AI
        if opponent.id == USER_ID_AI:
            if local_game:
                raise BarelyAnException(_("AI is above all, you can't play against it in a local game"))
            # TODO: issue #210
            raise BarelyAnException(_("Playing against AI is not supported yet"))
        # Check if there is already a direct game between the user and the opponent
        old_game = get_game_of_user(user, opponent)
        if old_game:
            return old_game, False

        # Create the game and the game members in a transaction
        with transaction.atomic():
            game = Game.objects.create(
                map_number=map_number,
                powerups=powerups,
            )
            game_member_user = GameMember.objects.create(
                game=game,
                user=user,
                local_game=local_game,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups,
                admin=True
            )
            game_member_opponent = GameMember.objects.create(
                game=game,
                user=opponent,
                local_game=local_game,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups,
                admin=False
            )
            game.save()
            game_member_user.save()
            game_member_opponent.save()
        if local_game:
            invite_msg = f"**GL,{game.as_clickable()}**"
        else:
            invite_msg = f"**G,{user.id},{opponent.id},{game.as_clickable()}**"
        create_and_send_overloards_pm(user, opponent, invite_msg)
        return game, True

def get_game_of_user(user1, user2):
    """
    This function returns the game between user1 and user2 if it exists.
    The game:
     - must be in a pending, ongoing or paused state.
     - can't be a tournament game.
    """
    user1_games = GameMember.objects.filter(
        user=user1.id,
        game__tournament_id=None,
        game__state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]
    ).values_list('game_id', flat=True)
    user2_games = GameMember.objects.filter(
        user=user2.id,
        game__tournament_id=None,
        game__state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]
    ).values_list('game_id', flat=True)
    if user1_games and user2_games:
        common_games = set(user1_games).intersection(user2_games)
        if common_games:
            game_id = common_games.pop()
            game = Game.objects.get(id=game_id)
            return game
    return None

def delete_game(user_id, game_id):
    # Check if the game exists
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        raise BarelyAnException(_("Game not found"))
    # Check if the user is a member of the game
    try:
        GameMember.objects.get(game=game_id, user=user_id)
    except GameMember.DoesNotExist:
        raise BarelyAnException(_("You are not a member of this game"), status_code=status.HTTP_403_FORBIDDEN)
    # Check for not being a tournament game
    if game.tournament_id:
        raise BarelyAnException(_("You can't delete a tournament game"))
    # Check if the game is in a deletable state
    if game.state != Game.GameState.PENDING:
        raise BarelyAnException(_("You can only delete a pending game"))
    # Delete the game and the game members in a transaction
    with transaction.atomic():
        GameMember.objects.filter(game=game_id).delete()
        game.delete()
    return True

def finish_game(game, message=None):
    logging.info(f"Finishing game {game.id}")
    game_members = GameMember.objects.filter(game=game.id)
    if not message:
        message = _(
                    "Game between {user1} and {user2} has been finished"
                ).format(
                    user1=game_members.first().user.username,
                    user2=game_members.last().user.username
                )
    with transaction.atomic():
        game.state = Game.GameState.FINISHED
        game.finish_time = timezone.now() #TODO: Issue #193
        game.save()
        if game_members.count() != 2:
            logging.error(f"Game {game.id} has not 2 members")
            return
        # Update the game members
        game_member_1 = GameMember.objects.select_for_update().get(id=game_members.first().id)
        game_member_2 = GameMember.objects.select_for_update().get(id=game_members.last().id)
        if game_member_1.points > game_member_2.points:
            game_member_1.result = GameMember.GameResult.WON
            game_member_2.result = GameMember.GameResult.LOST
        else:
            game_member_1.result = GameMember.GameResult.LOST
            game_member_2.result = GameMember.GameResult.WON
        game_member_1.save()
        game_member_2.save()

    winner = game_members.filter(result=GameMember.GameResult.WON).first()
    looser = game_members.filter(result=GameMember.GameResult.LOST).first()
    if not game.tournament_id:
        return winner, looser
    # Below is for tournament games only:
    send_ws_tournament_game_msg(game)
    # TODO: ??? #issue #339
    update_tournament_member_stats(game, winner, looser)
    update_tournament_ranks(game.tournament_id)
    check_tournament_routine(game.tournament_id)
    return winner, looser

def update_deadline_of_game(game_id):
    try:
        with transaction.atomic():
            game = Game.objects.select_for_update().get(id=game_id)

            if game.state != Game.GameState.PENDING:
                logging.info(f"ERROR: Game {game_id} is not in pending state")
                return

            if game.tournament_id is None:
                logging.info(f"ERROR: Game {game_id} is not a tournament game")
                return

            game.deadline = timezone.now() + DEADLINE_FOR_TOURNAMENT_GAME_START
            game.save()
        logging.info(f"Game {game.id} now has the deadline {game.deadline}")
        # Inform all users of the tournament
        send_ws_tournament_game_msg(game)
    except Game.DoesNotExist:
        logging.info(f"ERROR: Game {game_id} not found in function call update_deadline_of_game")
        return

def is_left_player(game_id, user_id):
    game_members = GameMember.objects.filter(game_id=game_id)
    if max(game_members.values_list('user_id', flat=True)) == user_id:
        return True
    else:
        return False

def get_user_of_game(game_id, side):
    game_members = GameMember.objects.filter(game_id=game_id)
    if side == "playerLeft":
        user_id_left = max(game_members.values_list('user_id', flat=True))
        return User.objects.get(id=user_id_left)
    elif side == "playerRight":
        user_id_right = min(game_members.values_list('user_id', flat=True))
        return User.objects.get(id=user_id_right)
    else:
        logging.error(f"! Side '{side}' is not valid has to be 'playerLeft' or 'playerRight'")
        return None
