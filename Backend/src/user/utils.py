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

def change_avatar(user, file_path):
    # Check if there's an existing avatar and delete it if it's not the default
    if user.avatar_path and user.avatar_path != "default_avatar.png":
        old_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', user.avatar_path)
        if default_storage.exists(old_avatar_path):
            default_storage.delete(old_avatar_path)
    
    # Update user's avatar_path field and save the user model
    user.avatar_path = file_path
    user.save()