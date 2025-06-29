from tournament.constants import MAX_LENGHT_OF_TOURNAMENT_NAME
from django.db import models

class Tournament(models.Model):
    class   TournamentState(models.TextChoices):
        SETUP = 'setup', 'Setup'
        ONGOING = 'ongoing', 'Ongoing'
        FINISHED = 'finished', 'Finished'

    id = models.AutoField(primary_key=True)
    state = models.CharField(
        max_length=8,
        choices=TournamentState.choices,
        default=TournamentState.SETUP
    )
    name = models.CharField(max_length=MAX_LENGHT_OF_TOURNAMENT_NAME)
    local_tournament = models.BooleanField()
    public_tournament = models.BooleanField()
    map_number = models.IntegerField()
    powerups = models.BooleanField()
    finish_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.state})"

    def as_clickable(self):
        return f"#T#{self.name}#{self.id}#"
    class Meta:
        db_table = '"barelyaschema"."tournament"'

class TournamentMember(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='tournaments')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='members')
    tournament_alias = models.CharField(max_length=150, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    played_games = models.IntegerField(default=0)
    won_games = models.IntegerField(default=0)
    win_points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.tournament_alias or self.user.username} in {self.tournament.name}"

    class Meta:
        db_table = '"barelyaschema"."tournament_member"'
        unique_together = ('user', 'tournament')

