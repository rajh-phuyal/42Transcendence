from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from user.models import User, NoCoolWith, IsCoolWith, CoolStatus

@receiver(post_save, sender=User)
def set_default_relationships(sender, instance, created, **kwargs):
    if created:  # This block will only run if the user instance is new
        try:
            # Block the new user by 'overloards'
            print("Creating default relationships for new user with id: ", instance.id)
            NoCoolWith.objects.create(blocker_id=1, blocked_id=instance.id)
            # Add AI Opponent as a friend with the new user
            IsCoolWith.objects.create(requester_id=2, requestee_id=instance.id, status=CoolStatus.ACCEPTED)
        except ObjectDoesNotExist as e:
            # Log or handle the exception if the user is missing
            print(f"Error in signal handler set_default_relationships: {e}")
