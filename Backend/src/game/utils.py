from django.utils.timezone import localtime
from tournament.constants import DEADLINE_FOR_TOURNAMENT_GAME_START
from tournament.tournament_manager import check_tournament_routine, update_tournament_ranks
from tournament.utils_ws import send_tournament_ws_msg
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from .models import Game, GameMember
from django.db.models import Q
from user.models import User
from core.exceptions import BarelyAnException
from user.exceptions import UserNotFound, RelationshipException, BlockingException
from user.utils_relationship import is_blocking, are_friends
from django.utils.translation import gettext as _
from user.constants import USER_ID_AI
import logging
from tournament.ranking import update_tournament_member_stats

def create_game(user_id, opponent_id, map_number, powerups, local_game):
        # Check if opponent exist
        try:
            user = User.objects.get(id=user_id)
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
            raise UserNotFound()
        # Check if opponent isn't urself, is ur friend and not blocking you
        if user_id == opponent_id:
            raise BarelyAnException(_("You can't play against yourself"))
        if not are_friends(user, opponent):
            raise RelationshipException(_("You can only play against your friends"))
        if is_blocking(opponent, user):
            raise BlockingException(_("Opponent is blocking you"))
        # Check if opponent is AI
        if opponent.id == USER_ID_AI:
            # TODO: issue #210
            logging.error("Playing against AI is not supported yet")
        # Check if there is already a direct game between the user and the opponent
        user_games = GameMember.objects.filter(
            user=user.id,
            game__tournament_id=None,
            game__state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]
        ).values_list('game_id', flat=True)
        opponent_games = GameMember.objects.filter(
            user=opponent.id,
            game__tournament_id=None,
            game__state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]
        ).values_list('game_id', flat=True)
        if user_games or opponent_games:
            common_games = set(user_games).intersection(opponent_games)
            if common_games:
                game_id = common_games.pop()
                return game_id, False

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
                powerup_slow = powerups
            )
            game_member_opponent = GameMember.objects.create(
                game=game,
                user=opponent,
                local_game=local_game,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups
            )
            game.save()
            game_member_user.save()
            game_member_opponent.save()
        return game.id, True

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

def finish_game(game, message):
    logging.info(f"Finishing game {game.id}")
    game_members = GameMember.objects.filter(game=game.id)
    if not message:
        message = _(
                    "Game between {user1} and {user2} has been finished"
                ).format(
                    user1=game_members.first().user.username,
                    user2=game_members.last().user.username
                )
    ...
    with transaction.atomic():
        game.state = Game.GameState.FINISHED
        game.finish_time = timezone.now() #TODO: Issue #193
        game.save()

    # For tournament games only:
    if not game.tournament_id:
        return
    # - inform everyone that the game finished
    winner = game_members.filter(result=GameMember.GameResult.WON).first()
    looser = game_members.filter(result=GameMember.GameResult.LOST).first()
    send_tournament_ws_msg(
        game.tournament_id,
        "gameUpdateState",
        "game_update_state",
        message,
        **{
            "gameId": game.id,
            "state": "finished",
            "winnerId": winner.user_id,
        }
    )
    update_tournament_member_stats(game, winner, looser)
    update_tournament_ranks(game.tournament_id)
    check_tournament_routine(game.tournament_id)

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
        send_tournament_ws_msg(
            game.tournament.id,
            "gameSetDeadline",
            "game_set_deadline",
            _("Game {game_id} has been set to pending. The deadline is {deadline}"
                ).format(
                    game_id=game.id,
                    deadline=localtime(game.deadline).isoformat()
                ),
            **{
                "gameId": game.id,
                "deadline": localtime(game.deadline).isoformat()
            }
        )
    except Game.DoesNotExist:
        logging.info(f"ERROR: Game {game_id} not found in function call update_deadline_of_game")
        return






# OLD:
# def start_game(map_number, powerups, tournament_id=None, deadline=None):
#     """
#     Initializes a new game in the 'pending' state.

#     :param map_number: Integer representing the map number for the game
#     :param powerups: Boolean, whether powerups are enabled
#     :param tournament_id: Optional integer, ID of the tournament this game is part of
#     :param deadline: Optional datetime, the deadline for the game
#     :return: The created Game instance
#     """
#     game = Game.objects.create(
#         map_number=map_number,
#         powerups=powerups,
#         tournament_id=tournament_id,
#         deadline=deadline
#     )
#     return game


# def get_active_games():
#     """
#     Retrieves all active games (i.e., those with state 'ongoing').

#     :return: QuerySet of active Game instances
#     """
#     return Game.objects.filter(state=Game.GameState.ONGOING)


# def get_game_by_id(game_id):
#     """
#     Retrieves a game by its ID.

#     :param game_id: Integer ID of the game
#     :return: Game instance if found, None otherwise
#     """
#     try:
#         return Game.objects.get(id=game_id)
#     except Game.DoesNotExist:
#         return None


# def add_game_member(game, user, local_game=False):
#     """
#     Adds a new member to a game.

#     :param game: Game instance
#     :param user: User instance representing the player
#     :param local_game: Boolean indicating if this is a local game
#     :return: The created GameMember instance
#     """
#     game_member = GameMember.objects.create(
#         game=game,
#         user=user,
#         local_game=local_game
#     )
#     return game_member


# def get_game_members(game_id):
#     """
#     Retrieves all members of a specific game.

#     :param game_id: Integer ID of the game
#     :return: QuerySet of GameMember instances
#     """
#     return GameMember.objects.filter(game_id=game_id)


# def update_game_state(game_id, new_state):
#     """
#     Updates the state of a game.

#     :param game_id: Integer ID of the game
#     :param new_state: New state to set for the game
#     :return: Boolean indicating if the update was successful
#     """
#     game = get_game_by_id(game_id)
#     if game and new_state in Game.GameState.values:
#         game.state = new_state
#         game.save()
#         return True
#     return False


# def finish_game(game_id):
#     """
#     Marks a game as finished and sets the finish time to the current time.

#     :param game_id: Integer ID of the game
#     :return: Boolean indicating if the game was successfully finished
#     """
#     game = get_game_by_id(game_id)
#     if game:
#         game.state = Game.GameState.FINISHED
#         game.finish_time = timezone.now()
#         game.save()
#         return True
#     return False


# def get_games_with_deadlines():
#     """
#     Retrieves games that have deadlines set.

#     :return: QuerySet of Game instances with deadlines
#     """
#     return Game.objects.filter(deadline__isnull=False)
