import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from user.models import IsCoolWith, NoCoolWith, CoolStatus
from user.exceptions import BlockingException

def is_blocking(doer, target):
    return NoCoolWith.objects.filter(blocker=doer, blocked=target).exists()
    
def is_blocked(doer, target):
    return NoCoolWith.objects.filter(blocker=target, blocked=doer).exists()
    
def check_blocking(requestee_id, requester_id):
    if is_blocked(requester_id, requestee_id):
        raise BlockingException(detail='You have been blocked by this user.')
    if is_blocking(requester_id, requestee_id):
        raise BlockingException(detail='You have blocked this user, you need to unblock them first.')
    
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
