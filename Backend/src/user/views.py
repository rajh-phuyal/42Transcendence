# Basics
import logging
# Django
from django.utils.translation import gettext as _, activate
from django.db import transaction
from rest_framework import status, viewsets
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
# Core
from core.decorators import barely_handle_exceptions
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
from core.exceptions import BarelyAnException
# Authentication
from authentication.utils import validate_username
# User
from user.constants import NO_OF_USERS_TO_LOAD, USER_ID_AI
from user.models import User, IsCoolWith
from user.serializers import ProfileSerializer, ListFriendsSerializer, SearchSerializer
from user.exceptions import ValidationException
from user.utils import get_user_by_id
from user.utils_img import process_avatar
from user.utils_relationship import is_blocking, block_user, unblock_user, send_request, accept_request, cancel_request, reject_request, unfriend
# Services
from services.chat_bots import send_message_with_delay
from asgiref.sync import async_to_sync

# SearchView for searching users by username
class SearchView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, search):
        if not search:
            error_response(_("key 'search' must be provided!"))
        onlyFriends = request.query_params.get('onlyFriends', 'false')
        current_user = request.user
        users = User.objects.filter(username__istartswith=search).exclude(id=current_user.id)
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

# ProfileView for retrieving a single user's profile by ID
class ProfileView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, targetUserId):
        try:
            user = User.objects.get(id=targetUserId)
        except User.DoesNotExist:
            return error_response(_("Profile not found"))
        serializer = ProfileSerializer(user, context={'request': request})
        return success_response(_("User profile loaded"), **serializer.data)

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
        logging.info(f"User: {user}, Target User: {target_user}")
        logging.info(f"is_blocking: {is_blocking(target_user, user)}")
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

        # Check if all fields are not empty
        if not new_username or not new_first_name or not new_last_name or not new_language:
            return error_response(_("All keys ('username', 'firstName', 'lastName', 'language') must be provided!"))

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
        user.username = new_username
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.language = new_language

        # Save the user object
        user.save()

        # Return the success response
        return success_response(_("User info updated"))