# Basics
import logging, random
# Celery
from celery import shared_task
# Django
from django.db import transaction
from django.utils.translation import gettext as _
from django.utils import timezone # Don't use from datetime import timezone, it will conflict with django timezone!
from asgiref.sync import async_to_sync
# Services
from services.send_ws_msg import send_ws_game_data_msg
# User
from user.constants import USER_ID_OVERLORDS, USER_ID_AI
# Tournament
from tournament.models import Tournament
from tournament.tournament_manager import check_tournament_routine
# Game
from game.models import Game, GameMember
from game.utils_ws import update_game_state
from game.AI import clear_ai_stats_cache
# CHAT
from chat.message_utils import create_and_send_overloards_pm

@shared_task(ignore_result=True)
def startup_check_deadline():
    logging.warning("STARTUP: Checking for overdue games aka ongoing tournaments")
    # Check all on-going tournaments and call the check_tournament_routine function
    ongoing_tournaments = Tournament.objects.filter(
        state=Tournament.TournamentState.ONGOING
    )
    for tournament in ongoing_tournaments:
        logging.warning(f"STARTUP: Checking tournament {tournament.id} ({tournament.name})")
        # Check if the tournament is finished
        check_tournament_routine(tournament.id)

@shared_task(ignore_result=True)
def check_overdue_tournament_games():
    # Check all games that have passed their deadline
    game_objects = Game.objects.filter(
        state__in=[Game.GameState.PENDING, Game.GameState.PAUSED],
        deadline__isnull=False
    )
    found_one = False
    current_time = timezone.now()
    for game in game_objects:
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
            # Set game to quited (this will also send the ws)
            async_to_sync(update_game_state)(game.id, Game.GameState.QUITED, USER_ID_OVERLORDS)
            async_to_sync(send_ws_game_data_msg)(game.id)

            # if the games as ai in it, clear the ai stats cache
            # asume ai is always the right player
            if game_members[1].user.id == USER_ID_AI:
                clear_ai_stats_cache(game.id)

    # if not found_one:
    #     logging.warning("Tournament Manager: No overdue games found.")


