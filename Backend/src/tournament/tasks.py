# Basics
import logging, random
# Celery
from celery import shared_task
# Django
from django.db import transaction
from django.utils.translation import gettext as _
from django.utils import timezone
# Tournament
from tournament.models import Tournament
# Game
from game.models import Game, GameMember
from game.utils import finish_game

@shared_task(ignore_result=True)
def check_overdue_tournament_games():
    # Check all tournament games that have passed their deadline
    active_tournaments_ids = Tournament.objects.filter(
        state=Tournament.TournamentState.ONGOING
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
                looser.points = 0
                looser.save()
                winner.points = 0
                winner.save()
            logging.info(f"Game {game.id} has passed its deadline. Decided: Winner is {winner.user_id} and looser is {looser.user_id}")
            #Set game to finished (this will also send the ws)
            finish_game(game, _("The overloards lost their patience. Game {gameId} has been set to finished since the deadline has passed. They randomly decided that user {username} won the game.")
                .format(gameId=game.id, username=winner.user.username))
    if not found_one:
        logging.info("No overdue games found.")


