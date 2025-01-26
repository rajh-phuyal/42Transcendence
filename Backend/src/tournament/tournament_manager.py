from django.utils.timezone import localtime
from itertools import combinations
from django.db import transaction
from tournament.models import Tournament, TournamentMember, TournamentState
from game.models import Game, GameMember
from core.exceptions import BarelyAnException
from tournament.utils import finish_tournament
from tournament.utils_ws import send_tournament_ws_msg
from tournament.serializer import TournamentGameSerializer
from tournament.constants import DEADLINE_FOR_TOURNAMENT_GAME_START
from django.utils import timezone
from django.utils.translation import gettext as _
import random
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
    check_tournament_routine(tournament.id)

# So there is one final in case the tournament has 3 members
# And there are four finals in case the tournament has more than 4 members
#   (2x semi-finals, final, third place)
# Note: this is only creating the games not the game members!
def create_final_games(tournament):
    logging.info(f"Creating final games for tournament {tournament.id}")
    amount_of_finals = 4
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
    if tournament_members.count() == 3:
        amount_of_finals = 1
    for i in range(amount_of_finals):
        # Create the final game(s)
        final_game = Game.objects.create(
            map_number=tournament.map_number,
            powerups=tournament.powerups,
            tournament_id=tournament.id
        )
        final_game.save()

def start_semi_finals(tournament, semi_finals):
    logging.info(f"Starting semi-finals for tournament {tournament.id}")
    # Get the players
    player_rank_1 = TournamentMember.objects.get(tournament_id=tournament.id, rank=1)
    player_rank_2 = TournamentMember.objects.get(tournament_id=tournament.id, rank=2)
    player_rank_3 = TournamentMember.objects.get(tournament_id=tournament.id, rank=3)
    player_rank_4 = TournamentMember.objects.get(tournament_id=tournament.id, rank=4)
    # Create the game member entrys
    with transaction.atomic():
        #   Semi-final 1:        1st vs 4th (Winner goes to final, Loser goes to third place game)
        game_member1 = GameMember.objects.create(
            user=player_rank_1.user,
            game=semi_finals[0],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member2 = GameMember.objects.create(
            user=player_rank_4.user,
            game=semi_finals[0],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )

        #   Semi-final 2:        2nd vs 3rd (Winner goes to final, Loser goes to third place game)
        game_member3 = GameMember.objects.create(
            user=player_rank_2.user,
            game=semi_finals[1],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member4 = GameMember.objects.create(
            user=player_rank_3.user,
            game=semi_finals[1],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        # Save the game member entrys
        game_member1.save()
        game_member2.save()
        game_member3.save()
        game_member4.save()
    data = TournamentGameSerializer(semi_finals, many=True).data
    for item in data:
        item['gameType'] = 'semi-final'
    send_tournament_ws_msg(
        tournament.id,
        "gameCreate",
        "game_create",
        f"Semi-Final Games have been created.",
        games=data
    )
    # Set the deadlines for the games
    update_deadlines(tournament, semi_finals)

def start_finals(tournament, all_finals):
    # We need to generate the final and the third place game
    # By setting their members and updating the deadlines
    logging.info(f"Starting finals for tournament {tournament.id}")
    final_player_1 =GameMember.objects.filter(
            game=all_finals[0].id,
            result=GameMember.GameResult.WON
        ).first().user
    final_player_2 = GameMember.objects.filter(
            game=all_finals[1].id,
            result=GameMember.GameResult.WON
        ).first().user
    third_place_player_1 = GameMember.objects.filter(
            game=all_finals[0].id,
            result=GameMember.GameResult.LOST
        ).first().user
    third_place_player_2 = GameMember.objects.filter(
            game=all_finals[1].id,
            result=GameMember.GameResult.LOST
        ).first().user
    with transaction.atomic():
        # Generate the third place game
        game_member1 = GameMember.objects.create(
            user=third_place_player_1,
            game=all_finals[2],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member2 = GameMember.objects.create(
            user=third_place_player_2,
            game=all_finals[2],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )

        # Generate the final game
        game_member3 = GameMember.objects.create(
            user=final_player_1,
            game=all_finals[3],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member4 = GameMember.objects.create(
            user=final_player_2,
            game=all_finals[3],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        # Save the game member entrys
        game_member1.save()
        game_member2.save()
        game_member3.save()
        game_member4.save()
    # Send websocket notifications to all tournament members
    data = TournamentGameSerializer([all_finals[2], all_finals[3]], many=True).data
    for item in data:
        if item['gameId'] == all_finals[2].id:
            item['gameType'] = 'third-place'
        else:
            item['gameType'] = 'final'
    send_tournament_ws_msg(
        tournament.id,
        "gameCreate",
        "game_create",
        f"Final Games have been created.",
        games=data
    )
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
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member2 = GameMember.objects.create(
            user=player_rank_2.user,
            game=final_game,
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member1.save()
        game_member2.save()
    # Send websocket notifications to all tournament members
    data = TournamentGameSerializer([final_game], many=True).data
    for item in data:
        item['gameType'] = 'final'
    send_tournament_ws_msg(
        tournament.id,
        "gameCreate",
        "game_create",
        f"Final Game {final_game.id} has been created.",
        games=data
    )
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
    if semi_finals[0].state != Game.GameState.FINISHED:
        logging.info(f"Case 2.1: Semi-final 1 is not finished yet")
        update_deadlines(tournament, final_games)
        return
    if semi_finals[1].state != Game.GameState.FINISHED:
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
    logging.info(f"User {user.username} has {ongoing_games} ongoing games and {deadline_games} games with a deadline and is {'available' if available else 'NOT available'} to play")
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
        logging.info(f"Checking game {game.id}")
        # Check if both users are free to play
        game_member1 = GameMember.objects.filter(game_id=game.id).select_related('user').first()
        game_member2 = GameMember.objects.filter(game_id=game.id).select_related('user').last()
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

# This will be called when a game is finished
# It will update the ranks of the tournament members and sned it as a sorted
# json list via ws to the tournament channel
def update_tournament_ranks(tournament_id):
    logging.info(f"Updating tournament ranks for tournament {tournament_id}")
    # Get the tournament
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        logging.error(f"in function call: update_tournament_ranks(): Tournament {tournament_id} not found")

    # Get all members of the tournament
    members = TournamentMember.objects.filter(tournament=tournament)

    # Calculate wins and point differences for each member
    member_stats = []
    for member in members:
        user = member.user
        games = GameMember.objects.filter(game__tournament=tournament, user=user)
        wins = member.won_games
        point_diff = member.win_points
        member_stats.append({
            'user_id': user.id,
            'username': user.username,
            'wins': wins,
            'point_diff': point_diff,
        })

    # Sort the stats: wins desc, point_diff desc, randomize ties
    sorted_stats = sorted(
        member_stats,
        key=lambda x: (x['wins'], x['point_diff'], random.random()),
        reverse=True
    )

    # Update the TournamentMember rank
    with transaction.atomic():
        for idx, stat in enumerate(sorted_stats, start=1):
            TournamentMember.objects.filter(
                user_id=stat['user_id'],
                tournament=tournament
            ).select_for_update(
            ).update(rank=idx)

    # Prepare the data for WebSocket broadcasting
    ranking_json = [
        {
            'userId': stat['user_id'],
            'wins': stat['wins'],
            'point_diff': stat['point_diff'],
            'rank': idx + 1
        }
        for idx, stat in enumerate(sorted_stats)
    ]

    # Send the ranking to the tournament channel
    send_tournament_ws_msg(
        tournament_id,
        "gameUpdateRank",
        "game_update_rank",
        _("The tournament ranking has been updated."),
        **{
            "ranking": ranking_json
        }
    )
