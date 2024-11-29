# from core.base_views import BaseAuthenticatedView
# from django.db import transaction
# from core.response import success_response, error_response
# from user.models import User
# from game.models import Game, GameMember
# from django.utils.translation import gettext as _, activate
# import logging
# from core.decorators import barely_handle_exceptions
# from .utils import start_game


# class CreateGameView(BaseAuthenticatedView):
#     @barely_handle_exceptions
#     def post(self, request):
#         # Get the user from the request
#         user = request.user
#         map_number = request.data.get('map_number')
#         powerups = request.data.get('powerups')
#         opponent_id = request.data.get('opponent')
#         opponent = User.objects.filter(id=opponent_id).first()

#         # 1. create a game and it always need 2 participants
#         with transaction.atomic():
#             game = start_game(map_number=map_number, powerups=powerups)
#             # game_member_1 = GameMember.objects.create(
#             #     game=game,
#             #     user=user,
#             #     local_game=False,
#             #     powerup_big = powerups,
#             #     powerup_fast = powerups,
#             #     powerup_slow = powerups
#             # )
            
#             # game_member_2 = GameMember.objects.create(
#             #     game=game,
#             #     user=opponent,
#             #     local_game=False,
#             #     powerup_big = powerups,
#             #     powerup_fast = powerups,
#             #     powerup_slow = powerups
#             # )
