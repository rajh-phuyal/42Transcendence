from itertools import combinations
from django.db import transaction
from tournament.models import Tournament, TournamentMember
from game.models import Game, GameMember
from core.exceptions import BarelyAnException
from tournament.utils_ws import send_tournament_ws_msg
from tournament.serializer import TournamentGameSerializer

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

    # Send websocket notifications to all members for each game created
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

