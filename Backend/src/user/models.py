from django.contrib.auth.models import AbstractUser
from django.db import models

# Table: barelyaschema.user
class User(AbstractUser):
    # We inherit the functionality of the AbstractUser class, which provides the
    # funcitonality of a user model, and change the table name to
    # "barelyaschema.user" which will be created form our 010_user.sql file
    # during the database container build.
    avatar_path = models.CharField(max_length=255, default='default_avatar.png', blank=True)
    language = models.CharField(max_length=5, default='en-US', blank=True)

    class Meta:
        db_table = '"barelyaschema"."user"'

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

    class Meta:
        db_table = '"barelyaschema"."is_cool_with"'
        unique_together = ('requester', 'requestee')  # Enforce the unique constraint in Django

# Table: barelyaschema.no_cool_with
class NoCoolWith(models.Model):
    id = models.AutoField(primary_key=True)
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocker_no_cool')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_no_cool')

    class Meta:
        db_table = '"barelyaschema"."no_cool_with"'
