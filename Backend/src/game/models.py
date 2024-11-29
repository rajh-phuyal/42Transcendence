from django.db import models

class Game(models.Model):
    class GameState(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ONGOING = 'ongoing', 'Ongoing'
        PAUSED = 'paused', 'Paused'
        FINISHED = 'finished', 'Finished'
        QUITED = 'quited', 'Quited'

    state = models.CharField(
        max_length=10,
        choices=GameState.choices,
        default=GameState.PENDING
    )
    map_number = models.IntegerField()
    powerups = models.BooleanField()
    tournament_id = models.IntegerField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Game {self.id} - State: {self.state}"
    
    class Meta:
        db_table = '"barelyaschema"."game"'


class GameMember(models.Model):
    class GameResult(models.TextChoices):
        PENDING = 'pending', 'Pending'
        WON = 'won', 'Won'
        LOST = 'lost', 'Lost'

    user = models.ForeignKey('barelyaschema.User', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    local_game = models.BooleanField()
    points = models.IntegerField(default=0)
    result = models.CharField(
        max_length=10,
        choices=GameResult.choices,
        default=GameResult.PENDING
    )
    powerup_big = models.BooleanField(default=False)
    powerup_fast = models.BooleanField(default=False)
    powerup_slow = models.BooleanField(default=False)

    def __str__(self):
        return f"GameMember {self.id} - User: {self.user_id} - Game: {self.game_id} - Result: {self.result}"
    
    class Meta:
        db_table = '"barelyaschema"."game_member"'