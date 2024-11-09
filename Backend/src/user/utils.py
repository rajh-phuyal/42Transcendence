import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.response import Response
from .models import User, IsCoolWith, NoCoolWith, CoolStatus
from .exceptions import ValidationException, BlockingException

def get_and_validate_data(request, action, target_name):

    doer = request.user
    # We don't need to check if doer is there because the user must be authenticated to reach this point
    
    # We extract the target from the JSON data
    target = request.data.get(target_name)
    if not target:
        raise ValidationException(f'Key --> "{target_name}".    {target_name} must be provided')

    # Check if the target is in a user table
    if not doer.__class__.objects.filter(id=target).exists():
        raise ValidationException(f'{target_name} not found')

    if doer.id == target:
        if action == 'remove':
            action = 'remov'

        raise ValidationException(f'{action}ing failed.  Cannot do it to yourself')
    
    return doer, target

def is_blocking(doer, target):
    return NoCoolWith.objects.filter(blocker=doer, blocked=target).exists()
    
def is_blocked(doer, target):
    return NoCoolWith.objects.filter(blocker=target, blocked=doer).exists()
    
def are_friends(doer, target):
    relation_1_2 = IsCoolWith.objects.filter(requester=doer, requestee=target, status=CoolStatus.ACCEPTED).exists()
    relation_2_1 = IsCoolWith.objects.filter(requester=target, requestee=doer, status=CoolStatus.ACCEPTED).exists()
    if relation_1_2 or relation_2_1:
        return True
    return False

def is_request_sent(doer, target):
    return IsCoolWith.objects.filter(requester=doer, requestee=target, status=CoolStatus.PENDING).exists()
    
def is_request_received(doer, target):
    return IsCoolWith.objects.filter(requester=target, requestee=doer, status=CoolStatus.PENDING).exists()

def check_blocking(requestee_id, requester_id):
    if is_blocked(requester_id, requestee_id):
        raise BlockingException(detail='You have been blocked by this user.')

    # Check if the requester has blocked the requestee
    if is_blocking(requester_id, requestee_id):
        raise BlockingException(detail='You have blocked this user, you need to unblock them first.')

# This checks the relationship status between two users
# from the perspective of requester towards requested
def get_relationship_status(requester, requested):
    # Initialize the variables for the return value
    state = "yourself"
    isBlocking = False
    isBlocked = False

    # Check if the users are the same
    if requester == requested:
        return {
            "state": state,
            "isBlocking": isBlocking,
            "isBlocked": isBlocked
        }

    # Check if there is a blocking relationship
    if is_blocking(requester, requested):
        isBlocking = True
    if is_blocked(requester, requested):
        isBlocked = True

    # Check for friendship
    if is_request_sent(requester, requested):
        state = "requestSent"
    elif is_request_received(requester, requested):
        state = "requestReceived"
    elif are_friends(requester, requested):
        state = "friend"
    else:
        state = "noFriend"

    # Return the relationship status
    return {
        "state": state,
        "isBlocking": isBlocking,
        "isBlocked": isBlocked
    }
def change_avatar(user, file_path):
    # Check if there's an existing avatar and delete it if it's not the default
    if user.avatar_path and user.avatar_path != "default_avatar.png":
        old_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', user.avatar_path)
        if default_storage.exists(old_avatar_path):
            default_storage.delete(old_avatar_path)
    
    # Update user's avatar_path field and save the user model
    user.avatar_path = file_path
    user.save()
