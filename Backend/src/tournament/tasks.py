from django.utils.translation import gettext as _
from celery import shared_task
from django.utils import timezone
from tournament.models import Tournament, TournamentState
from game.models import Game, GameMember
import logging
from django.db import transaction
import random
from tournament.tournament_manager import check_tournament_routine
from tournament.utils_ws import send_tournament_ws_msg
from game.utils import finish_game

@shared_task(ignore_result=True)
def check_overdue_tournament_games():
    # Check all tournament games that have passed their deadline
    active_tournaments_ids = Tournament.objects.filter(
        state=TournamentState.ONGOING
    ).values_list('id', flat=True)
    pending_games = Game.objects.filter(
        tournament_id__in=active_tournaments_ids,
        state=Game.GameState.PENDING,
        deadline__isnull=False
    )
    found_one = False
    current_time = timezone.now() #TODO: Issue #193
    for game in pending_games:
        if timezone.is_naive(game.deadline):
            game_deadline_aware = timezone.make_aware(game.deadline)
        else:
            game_deadline_aware = game.deadline

        # Compare the aware deadline with the current time
        if game_deadline_aware < current_time:
            found_one = True
            game_members = GameMember.objects.filter(game_id=game.id)
            # Random select a user to loose:TODO: implement a better logic
            looser=random.choice(game_members)
            winner=game_members.exclude(id=looser.id).first()
            with transaction.atomic():
                game=Game.objects.select_for_update().get(id=game.id)
                looser=GameMember.objects.select_for_update().get(id=looser.id)
                winner=GameMember.objects.select_for_update().get(id=winner.id)
                looser.result = GameMember.GameResult.LOST
                looser.points = 0
                looser.save()
                winner.result = GameMember.GameResult.WON
                winner.points = 11
                winner.save()
            logging.info(f"Game {game.id} has passed its deadline. Decided: Winner is {winner.user_id} and looser is {looser.user_id}")
            # Send websocket notification
            send_tournament_ws_msg(
                game.tournament_id,
                "gameUpdateScore",
                "game_update_score",
                _(
                    "Score updated game {gameId}. {usernameA} {pointsA}:{pointsB} {usernameB}")
                .format(
                    gameId=game.id,
                    usernameA=looser.user.username,
                    pointsA=looser.points,
                    pointsB=winner.points,
                    usernameB=winner.user.username
                ),
                **{
                    "gameId": game.id,
                    "state": None,
                    "score":{looser.user_id: looser.points, winner.user_id: winner.points},
                   }
            )
            #Set game to finished
            finish_game(game, _("The overloards lost their patience. Game {gameId} has been set to finished since the deadline has passed. They randomly decided that user {username} won the game.")
                .format(gameId=game.id, username=winner.user.username))
    # TODO: HACKATHON: Check if we can move this up for early return
    if not found_one:
        logging.info("No overdue games found.")


