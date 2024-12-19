from itertools import combinations
from django.db import transaction
from tournament.models import Tournament, TournamentMember, TournamentState
from game.models import Game, GameMember
from core.exceptions import BarelyAnException
from tournament.utils_ws import send_tournament_ws_msg
from tournament.serializer import TournamentGameSerializer
from tournament.constants import DEADLINE_FOR_TOURNAMENT_GAME_START
from django.utils import timezone
from django.utils.translation import gettext as _
import logging

# This creates the games for everyone against everyone in the tournament
# The deadline will be set later!
def create_initial_games(tournament, tournament_members):
    if len(tournament_members) < 2:
        # Should not happen, but just in case
        raise BarelyAnException("Cannot create games for less than 2 members.")

    # Generate all unique pairs of members
    member_pairs = combinations(tournament_members, 2)
    games_created = []

    # Wrap the creation process in a transaction to ensure atomicity
    with transaction.atomic():
        for member1, member2 in member_pairs:
            # Create the game
            game = Game.objects.create(
                map_number=tournament.map_number,
                powerups=tournament.powerups,
                tournament_id=tournament.id
            )

            # Add both members to the game
            GameMember.objects.create(
                user=member1.user,
                game=game,
                local_game=tournament.local_tournament,
                powerup_big=tournament.powerups,
                powerup_fast=tournament.powerups,
                powerup_slow=tournament.powerups
            )
            GameMember.objects.create(
                user=member2.user,
                game=game,
                local_game=tournament.local_tournament,
                powerup_big=tournament.powerups,
                powerup_fast=tournament.powerups,
                powerup_slow=tournament.powerups
            )

            games_created.append(game)

    # Send websocket notifications to all tournament members
    data = TournamentGameSerializer(games_created, many=True).data
    for item in data:
        item['gameType'] = 'normal' # since its not a semifinal or final or third place game
    send_tournament_ws_msg(
        tournament.id,
        "gameCreate",
        "game_create",
        f"Game {game.id} has been created.",
        games=data
    )

    # Set the deadline for the games
    check_if_new_games_can_have_a_deadline(tournament.id)

def is_user_available(user):
    # No ongoing/paused tournament games...
    ongoing_games = GameMember.objects.filter(
        user=user,
        game__state__in=[Game.GameState.ONGOING, Game.GameState.PAUSED],
        game__tournament_id__isnull=False
    ).count()
    #... and no deadline set
    deadline_games = GameMember.objects.filter(
        user=user,
        game__state=Game.GameState.PENDING,
        game__deadline__isnull=False
    ).count()
    if (ongoing_games + deadline_games) > 0:
        logging.info(f"User {user.username} is not available to play")
        return False
    logging.info(f"User {user.username} is available to play")
    return True

def check_if_new_games_can_have_a_deadline(tournament_id):
    logging.info("Checking if new games can have a deadline")
    # This will check all pending games and check if users are free to play
    pending_games = Game.objects.filter(
        tournament_id=tournament_id,
        state=Game.GameState.PENDING,
        deadline__isnull=True
    )

    # If no pending games are there create the finale, semi-final and third place games
    if not pending_games:
        #TODO:
        logging.info("No pending games found. Creating the final, semi-final and third place games. TODO")
        return

    # Update the deadline for all pending games
    for game in pending_games:
        logging.info(f"Checking game {game.id}")
        # Check if both users are free to play
        game_member1 = GameMember.objects.filter(game_id=game.id).select_related('user').first()
        game_member2 = GameMember.objects.filter(game_id=game.id).select_related('user').last()
        if not is_user_available(game_member1.user) or not is_user_available(game_member2.user):
            logging.info(f"User {game_member1.user.username} or {game_member2.user.username} is not available to play")
            continue
        # Both users are free to play so set the deadline
        with transaction.atomic():
            game = Game.objects.select_for_update().get(id=game.id)
            game.deadline = timezone.now() + DEADLINE_FOR_TOURNAMENT_GAME_START
            game.save()
        logging.info(f"Game {game.id} now has the deadline {game.deadline}")
        # Inform all users of the tournament
        send_tournament_ws_msg(
            tournament_id,
            "gameSetDeadline",
            "game_set_deadline",
            _("Game {game_id} has been set to pending. The deadline is {deadline}").format(game_id=game.id, deadline=game.deadline),
            **{
                "gameId": game.id,
                "deadline": game.deadline
            }
        )
