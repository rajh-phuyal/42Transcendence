# Basics
import logging
# Django
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.db.models import Q
from django.db import transaction
# User
from user.constants import USER_ID_OVERLORDS, USER_ID_AI, USER_ID_FLATMATE
from user.models import IsCoolWith, NoCoolWith
from user.exceptions import BlockingException
from user.exceptions import BlockingException, RelationshipException
# Chat
from chat.message_utils import create_and_send_overloards_pm
# Services
from services.send_ws_msg import send_ws_update_relationship

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
    relation_1_2 = IsCoolWith.objects.filter(requester=doer, requestee=target, status=IsCoolWith.CoolStatus.ACCEPTED).exists()
    relation_2_1 = IsCoolWith.objects.filter(requester=target, requestee=doer, status=IsCoolWith.CoolStatus.ACCEPTED).exists()
    if relation_1_2 or relation_2_1:
        return True
    return False

def is_request_sent(doer, target):
    return IsCoolWith.objects.filter(requester=doer, requestee=target, status=IsCoolWith.CoolStatus.PENDING).exists()

def is_request_received(doer, target):
    return IsCoolWith.objects.filter(requester=target, requestee=doer, status=IsCoolWith.CoolStatus.PENDING).exists()

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

# Logic for sending a friend request:
def send_request(user, target):
    if is_blocked(user, target):
        raise BlockingException(_('You have been blocked by this user'))
    if are_friends(user, target):
        raise RelationshipException(_('You are already friends with this user'))
    if is_request_sent(user, target) or is_request_received(user, target):
        raise RelationshipException(_('Friend request is already pending'))
    with transaction.atomic():
        cool_status = IsCoolWith(requester=user, requestee=target)
        cool_status.save()
    pm = "**FS,{requester_id},{requestee_id}**".format(requester_id=user.id, requestee_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)

# Logic for accepting a friend request:
def accept_request(user, target):
    if are_friends(user, target):
        raise RelationshipException(_('You are already friends with this user'))
    with transaction.atomic():
        try:
            cool_status = IsCoolWith.objects.select_for_update().get(requester=target, requestee=user, status=IsCoolWith.CoolStatus.PENDING)
        except ObjectDoesNotExist:
            raise RelationshipException(_('Friend request not found'))
        cool_status.status = IsCoolWith.CoolStatus.ACCEPTED
        cool_status.save()
    pm = "**FA,{requester_id},{requestee_id}**".format(requester_id=user.id, requestee_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)

# Logic for cancelling a friend request:
def cancel_request(user, target):
    if are_friends(user, target):
        raise RelationshipException(_('You are already friends with this user. Need to remove them as a friend instead.'))
    with transaction.atomic():
        try:
            cool_status = IsCoolWith.objects.select_for_update().get(requester=user, requestee=target, status=IsCoolWith.CoolStatus.PENDING)
        except ObjectDoesNotExist:
            raise RelationshipException(_('Friend request not found'))
        cool_status.delete()
    pm = "**FC,{requester_id},{requestee_id}**".format(requester_id=user.id, requestee_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)

# Logic for rejecting a friend request:
def reject_request(user, target):
    if are_friends(user, target):
        raise RelationshipException(_('You are already friends with this user. Need to remove them as a friend instead.'))
    with transaction.atomic():
        try:
            cool_status = IsCoolWith.objects.select_for_update().get(requester=target, requestee=user, status=IsCoolWith.CoolStatus.PENDING)
        except ObjectDoesNotExist:
            raise RelationshipException(_('Friend request not found'))
        cool_status.delete()
    pm = "**FR,{requester_id},{requestee_id}**".format(requester_id=user.id, requestee_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)

# Logic for removing a friend:
def unfriend(user, target):
    if target.id == USER_ID_AI or target.id == USER_ID_FLATMATE:
        raise RelationshipException(_('Computer says no'))
    with transaction.atomic():
        cool_status = IsCoolWith.objects.select_for_update().filter(
            (Q(requester=user) & Q(requestee=target)) |
            (Q(requester=target) & Q(requestee=user)),
            status=IsCoolWith.CoolStatus.ACCEPTED
        )
        if not cool_status:
            raise RelationshipException(_('You are not friends with this user'))
        cool_status.delete()
    pm = "**FU,{requester_id},{requestee_id}**".format(requester_id=user.id, requestee_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)

# Logic for blocking a user:
def block_user(user, target):
    if target.id == USER_ID_OVERLORDS:
        raise BlockingException(_('Try harder...LOL'))
    if target.id == USER_ID_AI or target.id == USER_ID_FLATMATE:
        raise BlockingException(_('Computer says no'))
    if is_blocking(user, target):
        raise BlockingException(_('You have already blocked this user'))
    with transaction.atomic():
        new_no_cool = NoCoolWith(blocker=user, blocked=target)
        new_no_cool.save()
    pm = "**B,{blocker_id},{blocked_id}**".format(blocker_id=user.id, blocked_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)

# Logic for unblocking a user:
def unblock_user(user, target):
    with transaction.atomic():
        try:
            no_cool = NoCoolWith.objects.select_for_update().get(blocker=user, blocked=target)
        except ObjectDoesNotExist:
            raise BlockingException(_('You have not blocked this user'))
        no_cool.delete()
    pm = "**U,{blocker_id},{blocked_id}**".format(blocker_id=user.id, blocked_id=target.id)
    send_ws_update_relationship(user, target)
    create_and_send_overloards_pm(user, target, pm)
