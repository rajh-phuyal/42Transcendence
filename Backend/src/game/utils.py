# Basics
import logging, random
# DJANGO
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _
from asgiref.sync import async_to_sync
# CORE
from core.exceptions import BarelyAnException
# SERVICES
from services.send_ws_msg import send_ws_tournament_game_msg, send_ws_all_tournament_members_msg, send_ws_game_data_msg
# USER
from user.constants import USER_ID_AI, USER_ID_OVERLORDS, USER_ID_FLATMATE
from user.models import User
from user.exceptions import RelationshipException, BlockingException
from user.utils_relationship import is_blocking, are_friends
# GAME
from game.constants import MAPNAME_TO_MAPNUMBER
from game.models import Game, GameMember
from game.game_cache import set_game_data, delete_game_from_cache, get_game_data
from game.utils_ws import update_game_state
# TOURNAMENT
from tournament.constants import DEADLINE_FOR_TOURNAMENT_GAME_START
from tournament.models import TournamentMember
from tournament.serializer import TournamentMemberSerializer
from tournament.tournament_manager import check_tournament_routine
from tournament.ranking import db_update_tournament_member_stats, db_update_tournament_ranks
from user.utils import get_user_by_id
# CHAT
from chat.message_utils import create_and_send_overloards_pm

def map_name_to_number(map_name):
    return MAPNAME_TO_MAPNUMBER.get(map_name.lower(), None)

def create_game(user, opponent_id, map_number, powerups):
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
        # Check if there is already a direct game between the user and the opponent
        old_game = get_game_of_user(user, opponent)
        if old_game:
            return old_game, False
        # Check if its with AI or Flatmate
        local_game = False
        if opponent.id in [USER_ID_AI, USER_ID_FLATMATE]:
            local_game = True
        # Create the game and the game members in a transaction
        with transaction.atomic():
            game = Game.objects.create(
                local_game=local_game,
                map_number=map_number,
                powerups=powerups,
            )
            game_member_user = GameMember.objects.create(
                game=game,
                user=user,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups,
            )
            game_member_opponent = GameMember.objects.create(
                game=game,
                user=opponent,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups,
            )
            game.save()
            game_member_user.save()
            game_member_opponent.save()
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

def delete_or_quit_game(user_id, game_id):
    logging.info(f"User {user_id} wants to delete/quit game {game_id}")
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
    opponent = GameMember.objects.filter(game=game_id).exclude(user=user_id).first().user


    # PENDING GAME - DELETE
    if game.state == Game.GameState.PENDING:
        # Inform the opponent
        gd = "**GD,{user_id},{game}**".format(user_id=user_id, game=game.as_clickable())
        create_and_send_overloards_pm(user_id, opponent, gd)
        # So if the other guy is in lobby to inform them
        set_game_data(game.id, 'gameData', 'state', 'aboutToBeDeleted')
        async_to_sync(send_ws_game_data_msg)(game_id)
        # And delete the game
        delete_game_from_cache(game_id)
        with transaction.atomic():
            GameMember.objects.filter(game=game_id).delete()
            game.delete()

    # ONGOING GAME - QUIT
    elif game.state == Game.GameState.ONGOING or game.state == Game.GameState.PAUSED or game.state == Game.GameState.COUNTDOWN:
        # ONGOING GAME - don't delete the game, just quit it
        gq = "**GQ,{user_id},{game}**".format(user_id=user_id, game=game.as_clickable())
        create_and_send_overloards_pm(user_id, opponent, gq)
        async_to_sync(update_game_state)(game_id, Game.GameState.QUITED, user_id)
        async_to_sync(send_ws_game_data_msg)(game_id)
    else:
        raise BarelyAnException(_("Game is already finished or quited"))
    return True

def end_game(game, quit_user_id=None):
    """
    This function should only be called by update_game_state function.

    If there is a quitter we set the state to QUITED if not to FINISHED.
    """

    game_members = GameMember.objects.filter(game=game.id)

    with transaction.atomic():
        if quit_user_id:
            game.state = Game.GameState.QUITED
        else:
            game.state = Game.GameState.FINISHED
        game.finish_time = timezone.now() #TODO: Issue #193
        game.save()
        if game_members.count() != 2:
            logging.error(f"Game {game.id} has not 2 members")
            return
        # Update the game members
        game_member_1 = GameMember.objects.select_for_update().get(id=game_members.first().id)
        game_member_2 = GameMember.objects.select_for_update().get(id=game_members.last().id)
        if quit_user_id:
            if quit_user_id == USER_ID_OVERLORDS:
                # If the the overlords decided that the game is - choose a winner
                # Random select a user to loose:TODO: implement a better logic
                if random.random() < 0.5:
                    game_member_1.result = GameMember.GameResult.LOST
                    game_member_2.result = GameMember.GameResult.WON
                else:
                    game_member_1.result = GameMember.GameResult.WON
                    game_member_2.result = GameMember.GameResult.LOST

            # The player who quits looses
            elif quit_user_id == game_member_1.user.id:
                game_member_1.result = GameMember.GameResult.LOST
                game_member_2.result = GameMember.GameResult.WON
            else:
                game_member_1.result = GameMember.GameResult.WON
                game_member_2.result = GameMember.GameResult.LOST
        else:
            # The player with more points wins
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
    # Below is for tournament games only:
    if not game.tournament:
        return winner, looser
    send_ws_tournament_game_msg(game)
    db_update_tournament_member_stats(game, winner, looser)
    if game.type == Game.GameType.NORMAL:
        db_update_tournament_ranks(game.tournament)
        # Send the updated tournament ranking to all users of the tournament
        send_ws_all_tournament_members_msg(game.tournament)
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
        # Send warning chat message to conversation of the two players
        player1_id = game.members.first().id
        player2_id = game.members.last().id
        tgw = "**TGW,{tournament_id},{game_id},{player1_id},{player2_id}**".format(
            tournament_id=game.tournament_id,
            game_id=game.id,
            player1_id=player1_id,
            player2_id=player2_id
        )
        create_and_send_overloards_pm(player1_id, player2_id, tgw)
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
