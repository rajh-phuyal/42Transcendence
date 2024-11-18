from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Enum for notification types
class NotificationType(models.TextChoices):
    FRIEND = 'friend', 'Friend'
    GAME = 'game', 'Game'
    TOURNAMENT = 'tournament', 'Tournament'

# Table: barelyaschema.notification
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=now, editable=False)
    seen_at = models.DateTimeField(null=True, blank=True)
    img_path = models.CharField(max_length=255)
    redir_path = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=NotificationType.choices)

    class Meta:
        db_table = '"barelyaschema"."notification"'
        ordering = ['-created_at']

    def mark_as_seen(self):
        """Mark the notification as seen."""
        self.seen_at = now()
        self.save()

    def __str__(self):
        return f"Notification: {self.title} for {self.user.username}"
