from django.contrib.auth.models import AbstractUser
from django.db import models
from core.exceptions import BarelyAnException
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _
from .constants import AVATAR_DEFAULT
from django.core.cache import cache
from services.constants import PRE_DATA_USER_ONLINE, PRE_CHANNEL_USER

# Table: barelyaschema.user
class User(AbstractUser):
    # We inherit the functionality of the AbstractUser class, which provides the
    # funcitonality of a user model, and change the table name to
    # "barelyaschema.user" which will be created form our 010_user.sql file
    # during the database container build.
    avatar_path = models.CharField(max_length=40, default=AVATAR_DEFAULT, blank=True)
    language = models.CharField(max_length=5, default='en-US', blank=True)

    class Meta:
        db_table = '"barelyaschema"."user"'

    def update_last_seen(self):
        self.last_login = timezone.now() #TODO: Issue #193
        self.save(update_fields=['last_login'])

    def set_online_status(self, status, channel_name=None):
        if status:
            cache.set(f'{PRE_DATA_USER_ONLINE}{self.id}', status, timeout=3000)  # 3000 seconds = 50 minutes
            cache.set(f'{PRE_CHANNEL_USER}{self.id}', channel_name, timeout=3000)
            # TODO:should be matched with the JWT token expiration time
            # And refresh if the client is still active or is calling an enpoint
        else:
            cache.delete(f'{PRE_DATA_USER_ONLINE}{self.id}')
            cache.delete(f'{PRE_CHANNEL_USER}{self.id}')
            self.update_last_seen()

    def get_online_status(self):
        return cache.get(f'{PRE_DATA_USER_ONLINE}{self.id}', default=False)

    def __str__(self):
        return f"id:{self.id}({self.username})"

# Table: barelyaschema.is_cool_with
class IsCoolWith(models.Model):
    class CoolStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'

    id = models.AutoField(primary_key=True)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requester_cool')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requestee_cool')
    status = models.CharField(max_length=10, choices=CoolStatus.choices, default=CoolStatus.PENDING)

    class Meta:
        db_table = '"barelyaschema"."is_cool_with"'
        unique_together = ('requester', 'requestee')

    def clean(self):
        if self.pk:
            return
        # Check for the existence of a reversed duplicate relationship (if new entry)
        if IsCoolWith.objects.filter(
            models.Q(requester=self.requester, requestee=self.requestee) |
            models.Q(requester=self.requestee, requestee=self.requester)
        ).exists():
            raise BarelyAnException(_('A relationship between these two users already exists.'))

    def save(self, *args, **kwargs):
        # Validate before saving
        self.clean()
        super().save(*args, **kwargs)

# Table: barelyaschema.no_cool_with
class NoCoolWith(models.Model):
    id = models.AutoField(primary_key=True)
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocker_no_cool')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_no_cool')

    class Meta:
        db_table = '"barelyaschema"."no_cool_with"'
        unique_together = ('blocker', 'blocked')
