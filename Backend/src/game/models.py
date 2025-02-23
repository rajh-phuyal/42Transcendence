# Basics
import logging
# Django
from django.db import models
from django.core.cache import cache
# User
from user.constants import USER_ID_AI, USER_ID_FLATMATE

class Game(models.Model):
    class GameState(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COUNTDOWN = 'countdown', 'Countdown'
        ONGOING = 'ongoing', 'Ongoing'
        PAUSED = 'paused', 'Paused'
        FINISHED = 'finished', 'Finished'
        QUITED = 'quited', 'Quited'

    class GameType(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        SEMI_FINAL = 'semifinal', 'Semifinal'
        THIRD_PLACE = 'thirdplace', 'Third Place'
        FINAL = 'final', 'Final'

    id = models.AutoField(primary_key=True)
    state = models.CharField(
        max_length=10,
        choices=GameState.choices,
        default=GameState.PENDING
    )
    type = models.CharField(
        max_length=11,
        choices=GameType.choices,
        default=GameType.NORMAL
    )
    local_game = models.BooleanField(default=False)
    map_number = models.IntegerField()
    powerups = models.BooleanField()
    tournament = models.ForeignKey('tournament.Tournament', null=True, blank=True, on_delete=models.SET_NULL, related_name='games')
    deadline = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Game {self.id} - State: {self.state}"

    def as_clickable(self):
        return f"#G#{self.id}#"

    class Meta:
        db_table = '"barelyaschema"."game"'

    def set_player_ready(self, userId, status):
        if userId in [USER_ID_AI, USER_ID_FLATMATE]:
            return
        if status:
            cache.set(f'game_{self.id}_user_{userId}_ready', status, timeout=3000)  # 3000 seconds = 50 minutes
            logging.info(f"User {userId} marked as ready for game {self.id}.")
        else:
            cache.delete(f'game_{self.id}_user_{userId}_ready')
            logging.info(f"User {userId} marked as not ready for game {self.id}.")

    def get_player_ready(self, userId):
        if userId in [USER_ID_AI, USER_ID_FLATMATE]:
            return True
        return cache.get(f'game_{self.id}_user_{userId}_ready', default=False)

class GameMember(models.Model):
    class GameResult(models.TextChoices):
        PENDING = 'pending', 'Pending'
        WON = 'won', 'Won'
        LOST = 'lost', 'Lost'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='game_members')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_members')
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
        return f"GameMember {self.id} - User: {self.user} - Game: {self.game} - Result: {self.result}"

    class Meta:
        db_table = '"barelyaschema"."game_member"'