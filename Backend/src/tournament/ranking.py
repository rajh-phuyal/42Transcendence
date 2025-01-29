from tournament.models import TournamentMember
from django.db import transaction


def updateCurrentRank(tournamentId):
    ...

# Only called when finishing a game
def update_tournament_member_stats(game, game_member_winner, game_member_looser):
    # 0. calculate point difference
    difference = game_member_winner.points - game_member_looser.points

    with transaction.atomic():
        # 1. get torunament_members
        tournament_member_winner = TournamentMember.objects.select_for_update().get(user_id=game_member_winner.user.id, tournament_id=game.tournament_id)
        tournament_member_looser = TournamentMember.objects.select_for_update().get(user_id=game_member_looser.user.id, tournament_id=game.tournament_id)

        # 2. update tournament_member stats
        tournament_member_looser.played_games += 1
        tournament_member_winner.played_games += 1
        tournament_member_winner.won_games += 1
        tournament_member_winner.win_points += difference
        tournament_member_winner.save()
        tournament_member_looser.save()

    # sendCurrentRankWS -> THIS WILL BE DONE BY FINISH GAME FUNCTION!