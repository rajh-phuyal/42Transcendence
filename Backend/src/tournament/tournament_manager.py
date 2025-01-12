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

def check_final_games_with_3_members(tournament, final_game):
    logging.info(f"Checking final game with 3 members for tournament {tournament.id}")

    # If the members are not set yet, set them
    try:
        final_members = GameMember.objects.filter(game_id=final_game.id)
        # This means the final game is already over (should not happen)
    except GameMember.DoesNotExist:
        # The final game is not over yet so it members need to be set
        player_rank_1 = TournamentMember.objects.get(tournament_id=tournament.id, finish_place=1)
        player_rank_2 = TournamentMember.objects.get(tournament_id=tournament.id, finish_place=2)
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
        update_deadlines(tournament.id, [final_game])

def start_semi_finals(tournament, semi_finals):
    # Get the players
    player_rank_1 = TournamentMember.objects.get(tournament_id=tournament.id, finish_place=1)
    player_rank_2 = TournamentMember.objects.get(tournament_id=tournament.id, finish_place=2)
    player_rank_3 = TournamentMember.objects.get(tournament_id=tournament.id, finish_place=3)
    player_rank_4 = TournamentMember.objects.get(tournament_id=tournament.id, finish_place=4)
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
    data = TournamentGameSerializer([semi_finals], many=True).data
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
    update_deadlines(tournament.id, semi_finals)

def start_finals(tournament, all_finals):
    # We need to generate the final and the third place game
    # By setting their members and updating the deadlines
    logging.info(f"Starting finals for tournament {tournament.id}")
    final_player_1 =GameMember.objects.filter(
            game=all_finals[0].id,
            result=GameMember.GameResult.WON
        )
    final_player_2 = GameMember.objects.filter(
            game=all_finals[1].id,
            result=GameMember.GameResult.WON
        )
    third_place_player_1 = GameMember.objects.filter(
            game=all_finals[0].id,
            result=GameMember.GameResult.LOST
        )
    third_place_player_2 = GameMember.objects.filter(
            game=all_finals[1].id,
            result=GameMember.GameResult.LOST
        )
    with transaction.atomic():
        # Generate the third place game
        game_member1 = GameMember.objects.create(
            user=third_place_player_1.user,
            game=all_finals[2],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member2 = GameMember.objects.create(
            user=third_place_player_2.user,
            game=all_finals[2],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )

        # Generate the final game
        game_member3 = GameMember.objects.create(
            user=final_player_1.user,
            game=all_finals[3],
            local_game=tournament.local_tournament,
            powerup_big=tournament.powerups,
            powerup_fast=tournament.powerups,
            powerup_slow=tournament.powerups
        )
        game_member4 = GameMember.objects.create(
            user=final_player_2.user,
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
        if item['id'] == all_finals[2].id:
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
    update_deadlines(tournament.id, all_finals[2:])

def check_final_games_with_more_than_3_members(tournament, final_games):
    logging.info(f"Checking final games with more than 3 members for tournament {tournament.id}")
    game_member_entrys_count = GameMember.objects.filter(game__in=final_games).count()
    if game_member_entrys_count == 0:
        # Case 1: No final game was played yet
        start_semi_finals(tournament, final_games[:2])
        return
    finals_finished = Game.objects.filter(tournament_id=tournament.id, state=Game.GameState.FINISHED).count()
    if finals_finished == 1:
        # Case 2: One final game was played (one of the semi-finals)
        logging.info(f"Case 2: One final game was played (one of the semi-finals)")
        # Just wait for the other semi-final to finish
        return
    if finals_finished == 2:
        # Case 3: Two final games were played (both semi-finals)
        logging.info(f"Case 3: Two final games were played (both semi-finals)")
        start_finals(tournament, final_games)
    else:
        # Case 4: Three final games were played (both semi-finals and either final or third place game)
        logging.info(f"Case 4: Three final games were played (both semi-finals and either final or third place game; Just wait for the other final game to finish)")

# So the finals are already created at this point but some games are still pending
def check_final_games(tournament):
    logging.info(f"Checking final games for tournament {tournament.id}")
    # So at this point the last (or last four games) are created
    final_games = Game.objects.filter(tournament_id=tournament.id).order_by('id').reverse()[:4]
    if final_games.count() == 1:
        check_final_games_with_3_members(tournament, final_games.first())
    else:
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
    if (ongoing_games + deadline_games) > 0:
        return False
    return True

def tournament_finals_started(tournament):
    # If there are not more games than everyone against everyone, then the final games havent started yet
    # this is the binomial coefficient
    total_games_count = Game.objects.filter(tournament_id=tournament.id).count()
    if total_games_count == len(tournament.tournament_members) * (len(tournament.tournament_members) - 1) / 2:
        return False
    return True

def update_deadlines(tournament_id, pending_games):
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

def check_tournament_routine(tournament_id):
    phase = "round_robin"
    if tournament_finals_started(tournament_id):
        phase = "finals"

    # This will check all pending games and check if users are free to play
    pending_games = Game.objects.filter(
        tournament_id=tournament_id,
        state=Game.GameState.PENDING,
        deadline__isnull=True
    )

    logging.info(f"Checking tournament {tournament_id} with phase {phase}")
    if phase == "finals":
        if pending_games:
            check_final_games(tournament_id)
        else:
            finish_tournament(tournament_id)
    else:
        # Phase is round robin
        if pending_games:
            update_deadlines(tournament_id, pending_games)
        else:
            create_final_games(tournament_id)
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
