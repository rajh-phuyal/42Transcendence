from rest_framework.response import Response
from .models import NoCoolWith
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


def check_blocking(requestee_id, requester_id):
    # Check if the requestee has blocked the requester
    requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id)
    if requestee_blocked.exists():
        raise BlockingException(detail='You have been blocked by this user.')

    # Check if the requester has blocked the requestee
    requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id)
    if requester_blocked.exists():
        raise BlockingException(detail='You have blocked this user, you need to unblock them first.')
