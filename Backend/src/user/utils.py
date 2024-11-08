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
    is_friendship = False
    relation_1_2 = IsCoolWith.objects.filter(requester=doer, requestee=target).first()
    relation_2_1 = IsCoolWith.objects.filter(requester=target, requestee=doer).first()
    if relation_1_2 or relation_1_2.status == CoolStatus.ACCEPTED:
        is_friendship = True
    return is_friendship

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
# from the perspective of user1 towards user2
def get_relationship_status(user1, user2):
    # Initialize the variables for the return value
    state = "yourself"
    isBlocking = False
    isBlocked = False

    # Check if the users are the same
    if user1 == user2:
        return {
            "state": state,
            "isBlocking": isBlocking,
            "isBlocked": isBlocked
        }

    # Default to no relationship
    state = "noFriend"

    # Check if there is a blocking relationship
    blocking_relationship = NoCoolWith.objects.filter(blocker=user1, blocked=user2).exists()
    blocked_by_relationship = NoCoolWith.objects.filter(blocker=user2, blocked=user1).exists()
    # Set the variables to True if the relationship exists
    if is_blocking(user1, user2):
        isBlocking = True
    if is_blocked(user1, user2):
        isBlocked = True

    # Check for friendship
    if are_friends(user1, user2):
        state = "friend"

    # Check for pending requests
    if is_request_sent(user1, user2):
        state = "requestSent"
    if is_request_received(user1, user2):
        state = "requestReceived"
    
    # Return the relationship status
    return {
        "state": state,
        "isBlocking": isBlocking,
        "isBlocked": isBlocked
    }
