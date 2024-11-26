from django.db import transaction
from django.utils import timezone
from django.db.models import F
from django.utils.translation import gettext as _
from user.constants import USER_ID_OVERLOARDS
from user.models import User
from django.db.models import Q
from .models import Message, ConversationMember

def mark_all_messages_as_seen(user_id, conversation_id):
    with transaction.atomic():
        new_messages = (
            Message.objects
            .select_for_update()
            .filter(conversation_id=conversation_id, seen_at__isnull=True)
            .exclude(user=user_id)
        )

        # Update messages
        new_messages.update(seen_at=timezone.now())

        # Update unread counter
        conversation_member = ConversationMember.objects.select_for_update().get(conversation_id=conversation_id, user=user_id)

        if conversation_member.unread_counter > 0:
            conversation_member.save(update_fields=['unread_counter'])

def get_conversation_name(user, conversation):
    if conversation.name:
        return conversation.name

    try:
        overlords = User.objects.get(id=USER_ID_OVERLOARDS)
        other_member = conversation.members.exclude(Q(user=user) | Q(user=overlords)).first()
        if other_member and other_member.user.username:
            return other_member.user.username
    except Exception:
        pass

    # Fallback to "Top Secret"
    return _("top secret")