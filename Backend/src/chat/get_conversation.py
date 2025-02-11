# Basics
# Django
# User
from user.models import User
# Chat
from chat.models import Conversation, ConversationMember, Message

# TODO: NEW AND REVIESD
def get_conversation_id(user1, user2):
    """ Accepts user  instances or IDs """
    if isinstance(user1, int):
        user1 = User.objects.get(id=user1)
    if isinstance(user2, int):
        user2 = User.objects.get(id=user2)

    # Conversations of user1
    user_conversations = ConversationMember.objects.filter(
        user=user1.id,
        conversation__is_group_conversation=False,
    ).values_list('conversation_id', flat=True)

    # Conversations of user2
    other_user_conversations = ConversationMember.objects.filter(
        user=user2.id,
        conversation__is_group_conversation=False
    ).values_list('conversation_id', flat=True)

    # Common conversations
    common_conversations = set(user_conversations).intersection(other_user_conversations)

    if common_conversations:
        return common_conversations.pop()
    return None

# this function will always return a valid conversation between two users
# it not exists, it will create a new one and add the "start of conversation" message
# TODO: NEW AND REVIESD
def get_conversation(user1, user2):
    """ Accepts user  instances or IDs """
    if isinstance(user1, int):
        user1 = User.objects.get(id=user1)
    if isinstance(user2, int):
        user2 = User.objects.get(id=user2)
    conversation_id = get_conversation_id(user1, user2)
    if conversation_id:
        return Conversation.objects.get(id=conversation_id)
    else:
        return create_conversation(user1, user2)

# Should only be called from function 'get_conversation'
def create_conversation(user1, user2):
    # TODO: thisfunction is not done!
    conversation = Conversation.objects.create(is_group_conversation=False)
    ConversationMember.objects.create(conversation=conversation, user=user1)
    ConversationMember.objects.create(conversation=conversation, user=user2)
    Message.objects.create(user=user1, conversation=conversation, content=_('Start of conversation'))
    return conversation