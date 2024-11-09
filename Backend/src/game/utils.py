from django.utils import timezone
from .models import Game, GameMember
from django.db.models import Q

def start_game(map_number, powerups, tournament_id=None, deadline=None):
    """
    Initializes a new game in the 'pending' state.

    :param map_number: Integer representing the map number for the game
    :param powerups: Boolean, whether powerups are enabled
    :param tournament_id: Optional integer, ID of the tournament this game is part of
    :param deadline: Optional datetime, the deadline for the game
    :return: The created Game instance
    """
    game = Game.objects.create(
        map_number=map_number,
        powerups=powerups,
        tournament_id=tournament_id,
        deadline=deadline
    )
    return game


def get_active_games():
    """
    Retrieves all active games (i.e., those with state 'ongoing').

    :return: QuerySet of active Game instances
    """
    return Game.objects.filter(state=Game.GameState.ONGOING)


def get_game_by_id(game_id):
    """
    Retrieves a game by its ID.

    :param game_id: Integer ID of the game
    :return: Game instance if found, None otherwise
    """
    try:
        return Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return None


def add_game_member(game, user, local_game=False):
    """
    Adds a new member to a game.

    :param game: Game instance
    :param user: User instance representing the player
    :param local_game: Boolean indicating if this is a local game
    :return: The created GameMember instance
    """
    game_member = GameMember.objects.create(
        game=game,
        user=user,
        local_game=local_game
    )
    return game_member


def get_game_members(game_id):
    """
    Retrieves all members of a specific game.

    :param game_id: Integer ID of the game
    :return: QuerySet of GameMember instances
    """
    return GameMember.objects.filter(game_id=game_id)


def update_game_state(game_id, new_state):
    """
    Updates the state of a game.

    :param game_id: Integer ID of the game
    :param new_state: New state to set for the game
    :return: Boolean indicating if the update was successful
    """
    game = get_game_by_id(game_id)
    if game and new_state in Game.GameState.values:
        game.state = new_state
        game.save()
        return True
    return False


def finish_game(game_id):
    """
    Marks a game as finished and sets the finish time to the current time.

    :param game_id: Integer ID of the game
    :return: Boolean indicating if the game was successfully finished
    """
    game = get_game_by_id(game_id)
    if game:
        game.state = Game.GameState.FINISHED
        game.finish_time = timezone.now()
        game.save()
        return True
    return False


def get_games_with_deadlines():
    """
    Retrieves games that have deadlines set.

    :return: QuerySet of Game instances with deadlines
    """
    return Game.objects.filter(deadline__isnull=False)
