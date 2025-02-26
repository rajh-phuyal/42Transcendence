# Basics
import logging, random
# Celery
from celery import shared_task
# Django
from django.db import transaction
from django.utils.translation import gettext as _
from django.utils import timezone
from asgiref.sync import async_to_sync
# Services
from services.send_ws_msg import send_ws_game_data_msg
# User
from user.constants import USER_ID_OVERLORDS
# Tournament
from tournament.models import Tournament
# Game
from game.models import Game, GameMember
from game.utils_ws import update_game_state
# CHAT
from chat.message_utils import create_and_send_overloards_pm

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
            # Inform the users
            game_members = GameMember.objects.filter(game=game)
            if not game_members.__len__() == 2:
                logging.error(f"Game {game.id} has {game_members.__len__()} members.")
                return
            gde = "**GDE,{game}**".format(game=game.as_clickable())
            create_and_send_overloards_pm(game_members[0].user, game_members[1].user, gde)
            # Set game to finished (this will also send the ws)
            async_to_sync(update_game_state)(game.id, Game.GameState.QUITED, USER_ID_OVERLORDS)
            async_to_sync(send_ws_game_data_msg)(game.id)
    if not found_one:
        logging.info("No overdue games found.")


