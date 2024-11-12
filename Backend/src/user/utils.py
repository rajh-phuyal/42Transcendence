import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.response import Response
from .models import User, IsCoolWith, NoCoolWith, CoolStatus
from .exceptions import ValidationException, BlockingException

def change_avatar(user, file_path):
    # Check if there's an existing avatar and delete it if it's not the default
    if user.avatar_path and user.avatar_path != "default_avatar.png":
        old_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', user.avatar_path)
        if default_storage.exists(old_avatar_path):
            default_storage.delete(old_avatar_path)
    
	# TODO: Add the atomic transaction here
    # Update user's avatar_path field and save the user model
    user.avatar_path = file_path
    user.save()
