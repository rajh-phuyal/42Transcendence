from django.db import models

from django.db import models

class TournamentState(models.TextChoices):
    SETUP = 'setup', 'Setup'
    ONGOING = 'ongoing', 'Ongoing'
    FINISHED = 'finished', 'Finished'

class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(
        max_length=8,
        choices=TournamentState.choices,
        default=TournamentState.SETUP
    )
    name = models.CharField(max_length=255)
    local_tournament = models.BooleanField()
    public_tournament = models.BooleanField()
    map_number = models.IntegerField()
    powerups = models.BooleanField()
    finish_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.state})"

    class Meta:
        db_table = '"barelyaschema"."tournament"'

class TournamentMember(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='tournament_members')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='members')
    tournament_alias = models.CharField(max_length=150, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    finish_place = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.tournament_alias or self.user.username} in {self.tournament.name}"
    
    class Meta:
        db_table = '"barelyaschema"."tournament_member"'
        unique_together = ('user', 'tournament')    

