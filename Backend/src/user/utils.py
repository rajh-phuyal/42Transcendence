# Basics
import os
# Django
from django.core.files.storage import default_storage
from django.conf import settings
from django.db import transaction
# User
from user.constants import AVATAR_DEFAULT
from user.models import User
from user.exceptions import UserNotFound

def change_avatar_in_db(user, file_path):
    # Check if there's an existing avatar and delete it if it's not the default
    if user.avatar_path and user.avatar_path != AVATAR_DEFAULT:
        old_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', user.avatar_path)
        if default_storage.exists(old_avatar_path):
            default_storage.delete(old_avatar_path)

    # Update user's avatar_path field and save the user model
    with transaction.atomic():
        user = User.objects.select_for_update().get(id=user.id)
        user.avatar_path = file_path
        user.save()

def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise UserNotFound
