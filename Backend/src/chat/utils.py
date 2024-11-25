from django.db import transaction
from django.utils import timezone
from django.db.models import F
from .models import Message

def mark_all_messages_as_seen(user_id, chat_id):
    with transaction.atomic():
        new_messages = (
            Message.objects
            .select_for_update()
            .filter(conversation_id=chat_id, seen_at__isnull=True)
            .exclude(user=user_id)
        )

        # Update messages
        updated_count = new_messages.update(seen_at=timezone.now())

        # Update 

    return updated_count
