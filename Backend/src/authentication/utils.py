import re
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_username(value):
    if not value:
        raise BarelyAnException(_("Username cannot be empty"))

    # Check for allowed characters
    if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
        raise BarelyAnException(_("Username can only contain letters, numbers, hyphens (-), and underscores (_)"))

    # Check if user already exists
    if User.objects.filter(username=value).exists():
        raise BarelyAnException((_("Username '{username}' already exists").format(username=value)))

    return value
