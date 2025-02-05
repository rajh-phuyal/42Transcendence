# Django
from django.utils.translation import gettext as _, activate
from django.db import transaction
from rest_framework import status
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
from user.constants import NO_OF_USERS_TO_LOAD
from user.models import User, IsCoolWith
from user.serializers import ProfileSerializer, ListFriendsSerializer, SearchSerializer
from user.exceptions import ValidationException
from user.utils import get_user_by_id
from user.utils_img import process_avatar
from user.utils_relationship import is_blocking, block_user, unblock_user, send_request, accept_request, cancel_request, reject_request, unfriend

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
            )
        # Limit the result
        users = users[:NO_OF_USERS_TO_LOAD]

        if not users:
            return success_response(_("No users found"), users=[])
        serializer = SearchSerializer(users, many=True)
        return success_response(_("The following users were found"), users=serializer.data)

# ProfileView for retrieving a single user's profile by ID
class ProfileView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, id):
        user = User.objects.get(id=id)
        serializer = ProfileSerializer(user, context={'request': request})
        return success_response(_("User profile loaded"), **serializer.data)

# =============================================================================
# ModifyFriendshipView for changing the relationship status between the
# authenticated user and another user ('target_id')
#
# Endpoint: /api/user/relationship/
#
# The possible actions are:
#  | METHOD    | ACTION    | ARGUMENTS             | USE CASE                 |
#  |-----------|-----------|-----------------------|--------------------------|
#  | POST      | 'send'    | 'action', 'target_id' | Send a friend request    |
#  | POST      | 'block'   | 'action', 'target_id' | Block a user             |
#  |           |           |                       |                          |
#  | PUT       | 'accept'  | 'action', 'target_id' | Accept a friend request  |
#  |           |           |                       |                          |
#  | DELETE    | 'cancel'  | 'action', 'target_id' | Cancel a friend request  |
#  | DELETE    | 'reject'  | 'action', 'target_id' | Reject a friend request  |
#  | DELETE    | 'remove'  | 'action', 'target_id' | Remove a friend          |
#  | DELETE    | 'unblock' | 'action', 'target_id' | Unblock a user           |
#
# =============================================================================
class RelationshipView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        allowed_actions = {'send', 'block'}
        user, target, action = self.validate_data(request, allowed_actions)
        if action == 'send':
            send_request(user, target)
            return success_response(_("Friend request sent"), status.HTTP_201_CREATED)
        elif action == 'block':
            block_user(user, target)
            return success_response(_("User blocked"), status.HTTP_201_CREATED)
        else:
            return error_response(self.return_unvalid_action_msg(request, allowed_actions), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    @barely_handle_exceptions
    def put(self, request):
        allowed_actions = {'accept'}
        user, target, action = self.validate_data(request, allowed_actions)
        if action == 'accept':
            accept_request(user, target)
            return success_response(_("Friend request accepted"))
        else:
            return error_response(self.return_unvalid_action_msg(request, allowed_actions), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    @barely_handle_exceptions
    def delete(self, request):
        allowed_actions = {'cancel', 'reject', 'remove', 'unblock'}
        user, target, action = self.validate_data(request, allowed_actions)
        if action == 'cancel':
            cancel_request(user, target)
            return success_response(_("Friend request cancelled"))
        elif action == 'reject':
            reject_request(user, target)
            return success_response(_("Friend request rejected"))
        elif action == 'remove':
            unfriend(user, target)
            return success_response(_("Friend removed"))
        elif action == 'unblock':
            unblock_user(user, target)
            return success_response(_("User unblocked"))
        else:
            return error_response(self.return_unvalid_action_msg(request, allowed_actions), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Utility function to validate that:
    # - the request data contains the required fields
    # - the action is one of the allowed actions
    # - the target user exists
    # - the target user is not the same as the authenticated user
    def validate_data(self, request, allowed_actions):
        user = request.user
        action = request.data.get('action')
        target_id = request.data.get('target_id')
        if not action:
            raise ValidationException(_("key 'action' must be provided!"))
        if action not in allowed_actions:
            raise ValidationException(self.return_unvalid_action_msg(request, allowed_actions), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        if not target_id:
            raise ValidationException(_("key 'target_id' must be provided!"))
        target = get_user_by_id(target_id) # This will trigger an exception if the user does not exist
        if user.id == target.id:
            raise ValidationException(_("cannot perform action on yourself"))
        return user, target, action

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
    def get(self, request, id):
        user = request.user
        target_user = User.objects.get(id=id)
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

        # Update the user info
        user.username = new_username
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.language = new_language

        # Save the user object
        user.save()

        # Return the success response
        return success_response(_("User info updated"))