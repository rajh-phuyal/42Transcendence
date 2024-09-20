from django.db import models

# Table: barelyaschema.user
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=False, default='this isn\'t a username but helpful for migration')
    # TODO: rename pswd to password before submitting. it does not work on Anatolii's machine for some reason
    pswd = models.CharField(max_length=255, null=False, default='this isn\'t a password but helpful for migration')

    class Meta:
        db_table = '"barelyaschema"."user"'

# Enum for friend request status (cool_status)
class CoolStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'

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
