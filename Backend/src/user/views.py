# Basics
import logging, html
# Django
from django.db.models import Q
from django.db import transaction
from django.utils.translation import gettext as _, activate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
# Core
from core.decorators import barely_handle_exceptions
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
# Authentication
from authentication.utils import validate_username
# User
from user.constants import NO_OF_USERS_TO_LOAD, USER_ID_AI, USER_ID_OVERLORDS
from user.models import User, IsCoolWith
from user.serializers import ProfileSerializer, ListFriendsSerializer, SearchSerializer
from user.exceptions import ValidationException
from user.utils import get_user_by_id
from user.utils_img import process_avatar
from user.utils_relationship import is_blocking, block_user, unblock_user, send_request, accept_request, cancel_request, reject_request, unfriend
# Services
from services.chat_bots import send_message_with_delay

# SearchView for searching users by username
class SearchView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, search):
        if not search:
            error_response(_("key 'search' must be provided!"))
        onlyFriends = request.query_params.get('onlyFriends', 'false')
        includeSelf = request.query_params.get('includeSelf', 'false')
        current_user = request.user
        users = User.objects.filter(username__istartswith=search)
        if includeSelf == 'false':
            users = users.exclude(id=current_user.id)
        if onlyFriends == 'true':
            # Filter to find users who have an ACCEPTED status in the 'IsCoolWith' table
            users = users.filter(
                Q(requester_cool__requestee=current_user, requester_cool__status=IsCoolWith.CoolStatus.ACCEPTED) |
                Q(requestee_cool__requester=current_user, requestee_cool__status=IsCoolWith.CoolStatus.ACCEPTED)
            ).distinct()
        # Limit the result
        users = users[:NO_OF_USERS_TO_LOAD]

        if not users:
            return success_response(_("No users found"), users=[])
        serializer = SearchSerializer(users, many=True)
        return success_response(_("The following users were found"), users=serializer.data)

# UsernameView for checking if a username exists for auth page
class UsernameView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # No authentication required for registration
    @barely_handle_exceptions
    def get(self, request, search):
        if not search:
            error_response(_("key 'search' must be provided!"))
        user = User.objects.filter(username=search)
        if user.exists():
            return success_response(_("Username exists"), exists=True)
        return success_response(_("Username does not exist"), exists=False)

    # Since we can't use BaseAuthenticatedView here, we need to handle the exceptions manually
    def post(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def head(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def options(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def trace(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

# ProfileView for retrieving a single user's profile by ID
class ProfileView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, targetUserId):
        try:
            target = User.objects.get(id=targetUserId)
        except User.DoesNotExist:
            return error_response(_("Profile not found"))
        serializer = ProfileSerializer(target, context={'request': request})
        data = serializer.data
        # If client is blocked remove all data but the username and the avatar
        if is_blocking(target, request.user):
           # logging.info(f"User: {request.user}, Target User: {target}")
            data['firstName'] = ''
            data['lastName'] = ''
            data['online'] = False
            data['lastLogin'] = None
            data['language'] = ''
            # data['chatId'] = '' Deliver the chat id so the client can redir to chat
            data['newMessage'] = False
            data['stats'] = ''
            # Send the notes only if the profile is of the overloards
            if target.id != USER_ID_OVERLORDS:
                data['notes'] = ''
        return success_response(_("User profile loaded"), **data)

class RelationshipView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request, action, targetUserId):
        """ Handles POST requests: send and block """
        action_map = {
            'send': lambda user, target: (send_request(user, target), _("Friend request sent")),
            'block': lambda user, target: (block_user(user, target), _("User blocked")),
        }
        if action not in action_map:
            return error_response(self.return_unvalid_action_msg(request, action_map.keys()), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        user, target = self.validate_not_urself(request, targetUserId)
        result, message = action_map[action](user, target)
        return success_response(message, status_code=status.HTTP_201_CREATED)

    @barely_handle_exceptions
    def put(self, request, action, targetUserId):
        """ Handles PUT requests: accept """
        action_map = {
            'accept': lambda user, target: (accept_request(user, target), _("Friend request accepted")),
        }
        if action not in action_map:
            return error_response(self.return_unvalid_action_msg(request, action_map.keys()), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        user, target = self.validate_not_urself(request, targetUserId)
        result, message = action_map[action](user, target)
        return success_response(message, status_code=status.HTTP_200_OK)

    @barely_handle_exceptions
    def delete(self, request, action, targetUserId):
        """ Handles DELETE requests: unblock, reject, cancel, remove """
        action_map = {
            'unblock': lambda user, target: (unblock_user(user, target), _("User unblocked")),
            'reject': lambda user, target: (reject_request(user, target), _("Friend request rejected")),
            'cancel': lambda user, target: (cancel_request(user, target), _("Friend request cancelled")),
            'remove': lambda user, target: (unfriend(user, target), _("Friend removed")),
        }
        if action not in action_map:
            return error_response(self.return_unvalid_action_msg(request, action_map.keys()), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        user, target = self.validate_not_urself(request, targetUserId)
        result, message = action_map[action](user, target)
        return success_response(message, status_code=status.HTTP_200_OK)

    def validate_not_urself(self, request, target_user_id):
        user = request.user
        target = get_user_by_id(target_user_id)
        if user.id == target.id:
            raise ValidationException(_("cannot perform action on yourself"))
        return user, target

    def return_unvalid_action_msg(self, request, allowed_actions):
        return _(
                "Invalid action! For method: {request_method}. "
                "Only the following actions are allowed: {allowed_actions}"
            ).format(
                request_method=request.method,
                allowed_actions=', '.join(allowed_actions)
            )

class ListFriendsView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, targetUserId):
        user = request.user
        target_user = get_user_by_id(targetUserId)
       # logging.info(f"User: {user}, Target User: {target_user}")
       # logging.info(f"is_blocking: {is_blocking(target_user, user)}")
        if is_blocking(target_user, user):
            return error_response(_("You are blocked by this user"), status_code=status.HTTP_403_FORBIDDEN)
        cool_with_entries = IsCoolWith.objects.filter(Q(requester=target_user) | Q(requestee=target_user))
        serializer = ListFriendsSerializer(cool_with_entries, many=True, context={'requester_user_id': user.id, 'target_user_id': target_user.id})
        return success_response(_("Friends list of user"), friends=serializer.data)

class UpdateAvatarView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request):
        if 'avatar' not in request.FILES:
            return error_response(_("key 'avatar' must be provided!"))
        avatar = request.FILES['avatar']
        result = process_avatar(request.user, avatar)
        return success_response(_("Avatar updated"), avatar_url=result)

class UpdateUserInfoView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request):
        # Get the user object
        user = request.user

        # Get the new user info from the request data
        new_username = request.data.get('username')
        new_first_name = request.data.get('firstName')
        new_last_name = request.data.get('lastName')
        new_language = request.data.get('language')
        new_notes = request.data.get('notes')
        # Prevent XSS attacks
        new_username = html.escape(new_username) if new_username else '' # Not needed since the username is validated
        new_first_name = html.escape(new_first_name) if new_first_name else ''
        new_last_name = html.escape(new_last_name) if new_last_name else ''
        new_language = html.escape(new_language) if new_language else '' # Not needed since the language is validated
        new_notes = html.escape(new_notes) if new_notes else ''

        # Check if the new username is valid
        if new_username != user.username:
            validate_username(new_username)

        # Check if the language is valid
        valid_languages = ['en-US', 'pt-PT', 'pt-BR', 'de-DE', 'uk-UA', 'ne-NP']
        if new_language not in valid_languages:
            error_response(_("Invalid / unsupported language code"))

        # Activate the new language
        activate(new_language)

        # Send a pm in the chat with AI
        if user.language != new_language:
            async_to_sync(send_message_with_delay)(USER_ID_AI, user, 0, _("Okay, I will now speak in ur new favorite language! ;)"))

        # Update the user info
        with transaction.atomic():
            # Update the user object
            if new_username != user.username:
                # Check if the username already exists
                if User.objects.filter(username=new_username).exists():
                    return error_response(_("Username already exists"))
                else:
                    user.username           = new_username
            if new_first_name != user.first_name:
                user.first_name         = new_first_name[:10]
            if new_last_name != user.last_name:
                user.last_name          = new_last_name[:10]
            if new_language != user.language:
                user.language           = new_language
            if new_notes != user.notes:
                user.notes              = new_notes[:600] if new_notes else ''

            # Save the user object
            user.save()

        # Return the success response in the new language
        activate(user.language)
        return success_response(_("User info updated"), **{'locale': user.language})