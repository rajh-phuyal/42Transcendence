# Basic
from itertools import combinations
import random, logging
# Django
from django.utils import timezone # Don't use from datetime import timezone, it will conflict with django timezone!
from django.utils.translation import gettext as _
from django.db import transaction
# Core
from core.exceptions import BarelyAnException
# Services
from services.send_ws_msg import send_ws_tournament_game_msg
# Tournament
from tournament.models import Tournament, TournamentMember
from tournament.utils import finish_tournament
# Game
from game.models import Game, GameMember
from game.serializer import GameSerializer

# This creates the games for everyone against everyone in the tournament
# The deadline will be set later!
def create_initial_games(tournament, tournament_members):
    if len(tournament_members) < 2:
        # Should not happen, but just in case
        raise BarelyAnException("Cannot create games for less than 2 members.")

    # Generate all unique pairs of members
    member_pairs = combinations(tournament_members, 2)

    # Wrap the creation process in a transaction to ensure atomicity
    with transaction.atomic():
        for member1, member2 in member_pairs:
            # Create the game
            game = Game.objects.create(
                local_game=tournament.local_tournament,
                map_number=tournament.map_number,
                powerups=tournament.powerups,
                tournament_id=tournament.id
            )

            # Add both members to the game
            GameMember.objects.create(
                user=member1.user,
                game=game,
                powerup_big=tournament.powerups,
                powerup_fast=tournament.powerups,
                powerup_slow=tournament.powerups
            )
            GameMember.objects.create(
                user=member2.user,
                game=game,
                powerup_big=tournament.powerups,
                powerup_fast=tournament.powerups,
                powerup_slow=tournament.powerups
            )
            # Send a ws message to tournament members
            send_ws_tournament_game_msg(game)
    # Set the deadline for the games
    check_tournament_routine(tournament.id)

# So there is one final in case the tournament has 3 members
# And there are four finals in case the tournament has more than 4 members
#   (2x semi-finals, final, third place)
# Note: this is only creating the games not the game members!
def create_final_games(tournament):
    # logging.info(f"Creating final games for tournament {tournament.id}")
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
    if tournament_members.count() == 3:
        # Only one final
        final_game = Game.objects.create(
            local_game=tournament.local_tournament,
            map_number=tournament.map_number,
            powerups=tournament.powerups,
            tournament_id=tournament.id,
            type=Game.GameType.FINAL
        )
        final_game.save()
    else:
        # Create the 4 last games:
        lastGames = [None] * 4
        for i in range(4):  # Correct loop syntax
            lastGames[i] = Game.objects.create(
                local_game=tournament.local_tournament,
                map_number=tournament.map_number,
                powerups=tournament.powerups,
                tournament_id=tournament.id
            )
        # Set the type of the games
        lastGames[0].type = Game.GameType.SEMI_FINAL
        lastGames[1].type = Game.GameType.SEMI_FINAL
        lastGames[2].type = Game.GameType.THIRD_PLACE
        lastGames[3].type = Game.GameType.FINAL
        # Save the games
        for game in lastGames:
            game.save()

def start_semi_finals(tournament, semi_finals):
    # logging.info(f"Starting semi-finals for tournament {tournament.id}")
    # Get the players
    player_rank_1 = TournamentMember.objects.get(tournament_id=tournament.id, rank=1)
    player_rank_2 = TournamentMember.objects.get(tournament_id=tournament.id, rank=2)
    player_rank_3 = TournamentMember.objects.get(tournament_id=tournament.id, rank=3)
    player_rank_4 = TournamentMember.objects.get(tournament_id=tournament.id, rank=4)
    # Create the game member entrys
    with transaction.atomic():
        #   Semi-final 1:        1st vs 4th (Winner goes to final, Loser goes to third place game)
        game_member1 = GameMember.objects.create(
            user = player_rank_1.user,
            game = semi_finals[0],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )
        game_member2  =  GameMember.objects.create(
            user = player_rank_4.user,
            game = semi_finals[0],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )

        #   Semi-final 2:        2nd vs 3rd (Winner goes to final, Loser goes to third place game)
        game_member3  =  GameMember.objects.create(
            user = player_rank_2.user,
            game = semi_finals[1],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )
        game_member4  =  GameMember.objects.create(
            user = player_rank_3.user,
            game = semi_finals[1],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )
        # Save the game member entrys
        game_member1.save()
        game_member2.save()
        game_member3.save()
        game_member4.save()
    # Send the ws message to tournament channel group to update the lobby
    send_ws_tournament_game_msg(semi_finals[0])
    send_ws_tournament_game_msg(semi_finals[1])
    # Set the deadlines for the games
    update_deadlines(tournament, semi_finals)

def start_finals(tournament, all_finals):
    # We need to generate the final and the third place game
    # By setting their members and updating the deadlines
    # logging.info(f"Starting finals for tournament {tournament.id}")
    final_player_1 = GameMember.objects.filter(
            game = all_finals[0].id,
            result = GameMember.GameResult.WON
        ).first().user
    final_player_2 = GameMember.objects.filter(
            game = all_finals[1].id,
            result = GameMember.GameResult.WON
        ).first().user
    third_place_player_1 = GameMember.objects.filter(
            game = all_finals[0].id,
            result=GameMember.GameResult.LOST
        ).first().user
    third_place_player_2 = GameMember.objects.filter(
            game = all_finals[1].id,
            result = GameMember.GameResult.LOST
        ).first().user
    with transaction.atomic():
        # Generate the third place game
        game_member1 = GameMember.objects.create(
            user = third_place_player_1,
            game = all_finals[2],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )
        game_member2  =  GameMember.objects.create(
            user = third_place_player_2,
            game = all_finals[2],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )

        # Generate the final game
        game_member3  =  GameMember.objects.create(
            user = final_player_1,
            game = all_finals[3],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )
        game_member4 = GameMember.objects.create(
            user = final_player_2,
            game = all_finals[3],
            powerup_big = tournament.powerups,
            powerup_fast = tournament.powerups,
            powerup_slow = tournament.powerups
        )
        # Save the game member entrys
        game_member1.save()
        game_member2.save()
        game_member3.save()
        game_member4.save()
    # Send websocket notifications to all tournament members to update the lobby
    send_ws_tournament_game_msg(all_finals[2])
    send_ws_tournament_game_msg(all_finals[3])
    #Set the deadlines for the games
    update_deadlines(tournament, all_finals[2:])

def check_final_games_with_3_members(tournament, final_game):
    logging.info(f"Checking final game with 3 members for tournament {tournament.id}")
    # The final game is not over yet so its members need to be set
    player_rank_1 = TournamentMember.objects.get(tournament_id=tournament.id, rank=1)
    player_rank_2 = TournamentMember.objects.get(tournament_id=tournament.id, rank=2)
    with transaction.atomic():
        game_member1 = GameMember.objects.create(
            user=player_rank_1.user,
            game=final_game,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member2 = GameMember.objects.create(
            user=player_rank_2.user,
            game=final_game,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member1.save()
        game_member2.save()
    # Send websocket notifications to all tournament members
    send_ws_tournament_game_msg(final_game)
    # Set the deadline for the game
    update_deadlines(tournament, [final_game])

def check_final_games_with_more_than_3_members(tournament, final_games):
    logging.info(f"Checking final games with more than 3 members for tournament {tournament.id}")
    semi_finals = final_games[:2] #Takes the first two
    semi_final_game_member_entrys_count = GameMember.objects.filter(game__in=semi_finals).count()
    if semi_final_game_member_entrys_count == 0:
        logging.info(f"Case 1: Semi-finals are not started yet -> Start them")
        start_semi_finals(tournament, semi_finals)
        return

    # Semi-finals are already started, check if both are finished
    logging.info(f"The semi-finals states are: {semi_finals[0].state} and {semi_finals[1].state}")
    # Need to check if it's not finished or quit
    if semi_finals[0].state not in [Game.GameState.FINISHED, Game.GameState.QUITED]:
        logging.info(f"Case 2.1: Semi-final 1 is not finished yet")
        update_deadlines(tournament, final_games)
        return
    if semi_finals[1].state not in [Game.GameState.FINISHED, Game.GameState.QUITED]:
        logging.info(f"Case 2.2: Semi-final 2 is not finished yet")
        update_deadlines(tournament, final_games)
        return

    # Check if the final games are already created (aka the game_member_entries)
    finals = final_games[2:] #Takes the last two
    final_game_member_entrys_count = GameMember.objects.filter(game__in=finals).count()
    if final_game_member_entrys_count == 0:
        logging.info(f"Case 3: Final games are not started yet -> Start them")
        start_finals(tournament, final_games)
        return

    # Check if the final games are finished aka just wait
    logging.info(f"The final games states are: {finals[0].state} and {finals[1].state}. We just need to wait until both are finished...")
    # For local games we need to update the deadlines again
    update_deadlines(tournament, final_games)

# So the finals are already created at this point but some games are still pending
def check_final_games(tournament):
    logging.info(f"Checking final games for tournament {tournament.id}")
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
    # So at this point the last (or last four games) are created
    if tournament_members.count() == 3:
        final_game = Game.objects.filter(tournament_id=tournament.id).order_by('-id').first()
        check_final_games_with_3_members(tournament, final_game)
    else:
        final_games = Game.objects.filter(tournament_id=tournament.id).order_by('-id')[:4][::-1]
        check_final_games_with_more_than_3_members(tournament, final_games)

def is_user_available(user):
    if not user:
        logging.error("is_user_available: user is None")
        return False
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
    available=True
    if (ongoing_games + deadline_games) > 0:
        available=False
    return available

def is_tournament_finals_started(tournament):
    # If there are not more games than everyone against everyone, then the final games havent started yet
    # this is the binomial coefficient
    total_games_count = Game.objects.filter(tournament_id=tournament.id).count()
    number_of_members = TournamentMember.objects.filter(tournament_id=tournament.id).count()
    if total_games_count == number_of_members * (number_of_members - 1) / 2:
        return False
    return True

def update_deadline_normal_tournament(tournament, pending_games):
    from game.utils import update_deadline_of_game
    logging.info(f"Tournament Manager logic: NORMAL for tournament {tournament.id}")
     # Update the deadline for all pending games
    for game in pending_games:
        # Check if both users are free to play
        game_member1 = GameMember.objects.filter(game_id=game.id).select_related('user').first()
        game_member2 = GameMember.objects.filter(game_id=game.id).select_related('user').last()
        if not game_member1 or not game_member2:
            logging.error(f"Game {game.id} has not 2 members")
            continue
        if not is_user_available(game_member1.user) or not is_user_available(game_member2.user):
            logging.info(f"User {game_member1.user.username} or {game_member2.user.username} is not available to play")
            continue
        # Both users are free to play so set the deadline
        logging.info(f"Both users ({game_member1.user.username} and {game_member2.user.username}) are available to play")
        update_deadline_of_game(game.id)

def update_deadline_local_tournament(tournament, pending_games):
    from game.utils import update_deadline_of_game
    logging.info(f"Tournament Manager logic: LOCAL for tournament {tournament.id}")
    # Just need to check if there is already another game ongoing or paused
    tournament_games_ongoing = Game.objects.filter(
        tournament_id=tournament.id,
        state__in=[Game.GameState.ONGOING, Game.GameState.PAUSED]
    ).count()
    if tournament_games_ongoing > 0:
        logging.info(f"Another game is already ongoing or paused")
        return
    # Check if another game already has a deadline
    tournament_games_with_deadline = Game.objects.filter(
        tournament_id=tournament.id,
        state=Game.GameState.PENDING,
        deadline__isnull=False
    ).count()
    if tournament_games_with_deadline > 0:
        logging.info(f"Another game already has a deadline")
        return
    # Update the deadline for a random pending game
    if not pending_games:
        logging.info(f"No pending games found - that is strange!")
    update_deadline_of_game(random.choice(pending_games).id)

def update_deadlines(tournament, pending_games):
    logging.info(f"Updating deadlines for tournament {tournament.id} with {len(pending_games)} pending games")

    # Just make sure pending_games is filtered correctly (could be important for local tournaments)
    pending_games = Game.objects.filter(
        id__in=[game.id for game in pending_games],
        tournament_id=tournament.id,
        deadline__isnull=True,
        state=Game.GameState.PENDING)

    if tournament.local_tournament:
        update_deadline_local_tournament(tournament, pending_games)
    else:
        update_deadline_normal_tournament(tournament, pending_games)

def check_tournament_routine(tournament_id):
    phase = "round_robin"
    tournament = Tournament.objects.get(id=tournament_id)
    if is_tournament_finals_started(tournament):
        phase = "finals"

    # This will check all pending games and check if users are free to play
    not_finished_games = Game.objects.filter(
        tournament_id=tournament_id,
        state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED],
    )
    not_finished_games_with_no_deadline = not_finished_games.filter(deadline__isnull=True)

    logging.info(f"Checking tournament {tournament_id} with phase {phase}")
    if phase == "finals":
        if not_finished_games:
            check_final_games(tournament)
        else:
            finish_tournament(tournament)
    else:
        # Phase is round robin
        if not_finished_games:
            update_deadlines(tournament, not_finished_games_with_no_deadline)
        else:
            create_final_games(tournament)
            check_tournament_routine(tournament_id)
