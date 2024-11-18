from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from .models import Notification

# Table: barelyaschema.user
class User(AbstractUser):
    # We inherit the functionality of the AbstractUser class, which provides the
    # funcitonality of a user model, and change the table name to
    # "barelyaschema.user" which will be created form our 010_user.sql file
    # during the database container build.
    avatar_path = models.CharField(max_length=40, default='54c455d5-761b-46a2-80a2-7a557d9ec618.png', blank=True)
    language = models.CharField(max_length=5, default='en-US', blank=True)

    class Meta:
        db_table = '"barelyaschema"."user"'

    def update_last_seen(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

# Enum for friend request status (cool_status)
class CoolStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'

# Table: barelyaschema.is_cool_with
class IsCoolWith(models.Model):
    id = models.AutoField(primary_key=True)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requester_cool')
    requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requestee_cool')
    status = models.CharField(max_length=10, choices=CoolStatus.choices, default=CoolStatus.PENDING)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True, related_name='cool_requests')

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
            raise ValidationError('A relationship between these two users already exists.')

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
