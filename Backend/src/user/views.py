from services.base_views import BaseAuthenticatedView
from services.response import success_response, error_response
import gettext as _
from django.db import transaction
from rest_framework import status
from django.db.models import Q
from .models import User, CoolStatus, IsCoolWith, NoCoolWith
from .serializers import ProfileSerializer, ListFriendsSerializer
from app.exceptions import BarelyAnException
from .exceptions import ValidationException, BlockingException, RelationshipException
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .utils_img import process_avatar
from .utils_relationship import is_blocking, is_blocked, check_blocking, are_friends, is_request_sent, is_request_received

# ProfileView for retrieving a single user's profile by ID
class ProfileView(BaseAuthenticatedView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'id'

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
    # 'send' a friend request
    # 'block' a user
    def post(self, request):
        allowed_actions = {'send', 'block'}
        try:
            user, target, action = self.validate_data(request, allowed_actions)
            if action == 'send':
                self.send_request(user, target)
                return success_response(_("Friend request sent"), status.HTTP_201_CREATED)
            elif action == 'block':
                self.block_user(user, target)
                return success_response(_("User blocked"), status.HTTP_201_CREATED)
            else:
                return error_response(self.return_unvalid_action_msg(request, allowed_actions))
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        except Exception as e:
            return error_response(str(e))

    # 'accept' a friend request
    def put(self, request):
        allowed_actions = {'accept'}
        try:
            user, target, action = self.validate_data(request, allowed_actions)
            if action == 'accept':
                self.accept_request(user, target)
                return success_response(_("Friend request accepted"))    
            else:
                return error_response(self.return_unvalid_action_msg(request, allowed_actions))
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        except Exception as e:
            return error_response(str(e))
        
    # 'cancel'  a friend request
    # 'reject'  a friend request
    # 'remove'  a friend
    # 'unblock' a user
    def delete(self, request):
        allowed_actions = {'cancel', 'reject', 'remove', 'unblock'}
        try:
            user, target, action = self.validate_data(request, allowed_actions)
            if action == 'cancel':
                self.cancel_request(user, target)
                return success_response(_("Friend request cancelled"))
            elif action == 'reject':
                self.reject_request(user, target)
                return success_response(_("Friend request rejected"))
            elif action == 'remove':
                self.remove_friend(user, target)
                return success_response(_("Friend removed"))
            elif action == 'unblock':
                self.unblock_user(user, target)
                return success_response(_("User unblocked"))
            else:
                return error_response(self.return_unvalid_action_msg(request, allowed_actions))
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        except Exception as e:
            return error_response(str(e))

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
            raise ValidationException(self.return_unvalid_action_msg(request, allowed_actions))
        if not target_id:
            raise ValidationException(_("key 'target_id' must be provided!"))
        target = User.objects.get(id=target_id)
        if not target:
            raise ValidationException(_("user with 'target_id' not found"))
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

    # Logic for sending a friend request:
    def send_request(self, user, target):
        if is_blocked(user, target):
            raise BlockingException(_('You have been blocked by this user'))
        if are_friends(user, target):
            raise RelationshipException(_('You are already friends with this user'))
        if is_request_sent(user, target) or is_request_received(user, target):
            raise RelationshipException(_('Friend request is already pending'))
        cool_status = IsCoolWith(requester=user, requestee=target)
        cool_status.save()

    # Logic for blocking a user:
    def block_user(self, user, target):
        if target.id == 1:
            raise BlockingException(_('Try harder...LOL'))
        if target.id == 2:
            raise BlockingException(_('Computer says no'))
        if is_blocking(user, target):
            raise BlockingException(_('You have already blocked this user'))
        new_no_cool = NoCoolWith(blocker=user, blocked=target)
        new_no_cool.save()
    
    # Logic for accepting a friend request:
    def accept_request(self, user, target):
        if are_friends(user, target):
            raise RelationshipException(_('You are already friends with this user'))
        with transaction.atomic():
            try:
                cool_status = IsCoolWith.objects.select_for_update().get(requester=target, requestee=user, status=CoolStatus.PENDING)
            except ObjectDoesNotExist:
                raise RelationshipException(_('Friend request not found'))
            cool_status.status = CoolStatus.ACCEPTED
            cool_status.save()
    
    # Logic for cancelling a friend request:
    def cancel_request(self, user, target):
        if are_friends(user, target):
            raise RelationshipException(_('You are already friends with this user. Need to remove them as a friend instead.'))
        with transaction.atomic():
            try:
                cool_status = IsCoolWith.objects.select_for_update().get(requester=user, requestee=target, status=CoolStatus.PENDING)
            except ObjectDoesNotExist:
                raise RelationshipException(_('Friend request not found'))
            cool_status.delete()

    # Logic for rejecting a friend request:
    def reject_request(self, user, target):
        if are_friends(user, target):
            raise RelationshipException(_('You are already friends with this user. Need to remove them as a friend instead.'))
        with transaction.atomic():
            try:
                cool_status = IsCoolWith.objects.select_for_update().get(requester=target, requestee=user, status=CoolStatus.PENDING)
            except ObjectDoesNotExist:
                raise RelationshipException(_('Friend request not found'))
            cool_status.delete()

    # Logic for removing a friend:
    def remove_friend(self, user, target):
        if target.id == 2:
            raise RelationshipException(_('Computer says no'))
        with transaction.atomic():
            cool_status = IsCoolWith.objects.select_for_update().filter(
                (Q(requester=user) & Q(requestee=target)) |
                (Q(requester=target) & Q(requestee=user)),
                status=CoolStatus.ACCEPTED
            )
            if not cool_status:
                raise RelationshipException(_('You are not friends with this user'))
            cool_status.delete()
    
    # Logic for unblocking a user:
    def unblock_user(self, user, target):
        with transaction.atomic():
            try:
                no_cool = NoCoolWith.objects.select_for_update().get(blocker=user, blocked=target)
            except ObjectDoesNotExist:
                raise BlockingException(_('You have not blocked this user'))
            no_cool.delete()

class ListFriendsView(BaseAuthenticatedView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            error_response(_("User not found"), status.HTTP_404_NOT_FOUND)
        cool_with_entries = IsCoolWith.objects.filter(Q(requester=user) | Q(requestee=user))
        serializer = ListFriendsSerializer(cool_with_entries, many=True, context={'user_id': user.id})
        return success_response(_("Friends list of user"), friends=serializer.data)
   
class UpdateAvatarView(BaseAuthenticatedView):
    def post(self, request):
        # Check if 'avatar' is in request.FILES
        if 'avatar' not in request.FILES:
            return error_response(_("key 'avatar' must be provided!"))

        # Get the avatar file from request.FILES
        avatar = request.FILES['avatar']

        # Call the utility function to process the avatar
        try:
            result = process_avatar(request.user, avatar)
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        except Exception as e:
            return error_response(str(e))

        # Return the success response with the avatar URL
        return success_response(_("Avatar updated"), avatar_url=result)
    
class UpdateUserInfoView(BaseAuthenticatedView):
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
            error_response(_("All key ('username', 'firstName', 'lastName', 'language') must be provided!"))
            
        # Check if the new username is valid
        # TODO: Wait for issue #108

        # Check if the language is valid
        valid_languages = ['en-US', 'pt-PT', 'pt-BR', 'de-DE', 'uk-UA', 'ne-NP']
        if new_language not in valid_languages:
            error_response(_("Invalid / unsupported language code"))
        
        # Update the user info
        user.username = new_username
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.language = new_language

        # Save the user object
        try:
            user.save()
        except Exception as e:
            return error_response(str(e))

        # Return the success response
        return success_response(_("User info updated"))