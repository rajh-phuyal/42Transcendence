from chat.models import Message, Conversation
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()

@sync_to_async
def save_message(conversation_id, sender_id, content):
    conversation = Conversation.objects.get(id=conversation_id)
    sender = User.objects.get(id=sender_id)
    return Message.objects.create(conversation=conversation, user=sender, content=content)

@sync_to_async
def get_conversation_messages(conversation_id):
    return list(
        Message.objects.filter(conversation_id=conversation_id).order_by("created_at").values(
            "id", "user_id", "content", "created_at"
        )
    )
