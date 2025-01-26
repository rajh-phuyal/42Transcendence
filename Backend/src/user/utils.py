import os
from django.core.files.storage import default_storage
from django.conf import settings

def change_avatar_in_db(user, file_path):
    # Check if there's an existing avatar and delete it if it's not the default
    if user.avatar_path and user.avatar_path != "54c455d5-761b-46a2-80a2-7a557d9ec618.png":
        old_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars/', user.avatar_path)
        if default_storage.exists(old_avatar_path):
            default_storage.delete(old_avatar_path)

	# TODO: Add the atomic transaction here
    # Update user's avatar_path field and save the user model
    user.avatar_path = file_path
    user.save()