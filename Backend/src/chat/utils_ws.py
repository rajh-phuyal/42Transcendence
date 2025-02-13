# Django
from django.utils.translation import gettext as _
from channels.db import database_sync_to_async
# Chat
from chat.utils import validate_conversation_membership, get_other_user

@database_sync_to_async
def validate_conversation_membership_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    validate_conversation_membership(user, conversation)

@database_sync_to_async
def get_other_user_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    return get_other_user(user, conversation)
