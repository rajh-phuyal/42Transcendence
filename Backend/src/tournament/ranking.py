from tournament.models import TournamentMember
from django.db.models import F, ExpressionWrapper, FloatField, Case, When, Value
from django.db import transaction

# Only called when finishing a game
def db_update_tournament_member_stats(game, game_member_winner, game_member_looser):
    # Only update if its a round robin game! aka Game.GameType.NORMAL
    if game.type != 'normal':
        return
    # 0. calculate point difference
    difference = game_member_winner.points - game_member_looser.points

    with transaction.atomic():
        # 1. get tournament_members
        tournament_member_winner = TournamentMember.objects.select_for_update().get(user_id=game_member_winner.user.id, tournament_id=game.tournament_id)
        tournament_member_looser = TournamentMember.objects.select_for_update().get(user_id=game_member_looser.user.id, tournament_id=game.tournament_id)

        # 2. update tournament_member stats
        # LOOSER
        tournament_member_looser.played_games += 1
        tournament_member_looser.save()
        # WINNER
        tournament_member_winner.played_games += 1
        tournament_member_winner.won_games += 1
        tournament_member_winner.win_points += difference
        tournament_member_winner.save()

# This will be called when a game is finished
# It will update the ranks of the tournament members
def db_update_tournament_ranks(tournament):
    # Sort descending by ratio won_games / played_games and win_points
    members = TournamentMember.objects.filter(tournament=tournament).annotate(
        # Ensure that win_ratio is properly handled for cases where played_games is zero
        win_ratio=Case(
            When(played_games=0, then=Value(0.0)),  # Explicitly set to 0 when no games played
            default=ExpressionWrapper(F('won_games') * 1.0 / F('played_games'), output_field=FloatField()),
            output_field=FloatField()
        )
    ).order_by('-win_ratio', '-win_points')

    with transaction.atomic():
        for rank, member in enumerate(members, start=1):
            member.rank = rank
            member.save(update_fields=['rank'])
