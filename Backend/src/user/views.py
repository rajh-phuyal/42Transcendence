from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q
from .models import User, CoolStatus, IsCoolWith, NoCoolWith
from .serializers import ProfileSerializer, ListFriendsSerializer
from .exceptions import ValidationException, BlockingException, RelationshipException
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os
from .utils_img import process_avatar
from .utils_relationship import is_blocking, is_blocked, check_blocking, are_friends, is_request_sent, is_request_received

# ProfileView for retrieving a single user's profile by ID
class ProfileView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
class RelationshipView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # 'send' a friend request
    # 'block' a user
    def post(self, request):
        allowed_actions = {'send', 'block'}
        try:
            user, target, action = self.validate_data(request, allowed_actions)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if action == 'send':
                self.send_request(user, target)
                return Response({'success': 'Friend request sent'}, status=status.HTTP_201_CREATED)
            elif action == 'block':
                self.block_user(user, target)
                return Response({'success': 'User blocked'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': request.method + ' error on endpoint /api/user/relationship/'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # 'accept' a friend request
    def put(self, request):
        allowed_actions = {'accept'}
        try:
            user, target, action = self.validate_data(request, allowed_actions)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if action == 'accept':
                self.accept_request(user, target)
                return Response({'success': 'Friend request accepted'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': request.method + ' error on endpoint /api/user/relationship/'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # 'cancel'  a friend request
    # 'reject'  a friend request
    # 'remove'  a friend
    # 'unblock' a user
    def delete(self, request):
        allowed_actions = {'cancel', 'reject', 'remove', 'unblock'}
        try:
            user, target, action = self.validate_data(request, allowed_actions)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if action == 'cancel':
                self.cancel_request(user, target)
                return Response({'success': 'Friend request cancelled'}, status=status.HTTP_200_OK)
            elif action == 'reject':
                self.reject_request(user, target)
                return Response({'success': 'Friend request rejected'}, status=status.HTTP_200_OK)
            elif action == 'remove':
                self.remove_friend(user, target)
                return Response({'success': 'Friend removed'}, status=status.HTTP_200_OK)
            elif action == 'unblock':
                self.unblock_user(user, target)
                return Response({'success': 'User unblocked'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': request.method + ' error on endpoint /api/user/relationship/'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
            raise ValidationException('`action` must be provided')
        if action not in allowed_actions:
            raise ValidationException('Invalid action! for method: ' + request.method + '. only the following actions are allowed: ' + ', '.join(allowed_actions))
        if not target_id:
            raise ValidationException('`target_id` must be provided')
        target = User.objects.get(id=target_id)
        if not target:
            raise ValidationException('user with `target_id` not found')
        if user.id == target.id:
            raise ValidationException('cannot perform action on yourself')
        return user, target, action
    
    # Logic for sending a friend request:
    def send_request(self, user, target):
        if is_blocked(user, target):
            raise BlockingException('You have been blocked by this user')
        if are_friends(user, target):
            raise RelationshipException('You are already friends with this user')
        if is_request_sent(user, target) or is_request_received(user, target):
            raise RelationshipException('Friend request is already pending')
        cool_status = IsCoolWith(requester=user, requestee=target)
        cool_status.save()

    # Logic for blocking a user:
    def block_user(self, user, target):
        if target.id == 1:
            raise BlockingException('Try harder...LOL')
        if target.id == 2:
            raise BlockingException('Computer says no')
        if is_blocking(user, target):
            raise BlockingException('You have already blocked this user')
        new_no_cool = NoCoolWith(blocker=user, blocked=target)
        new_no_cool.save()
    
    # Logic for accepting a friend request:
    def accept_request(self, user, target):
        if are_friends(user, target):
            raise RelationshipException('You are already friends with this user')
        with transaction.atomic():
            try:
                cool_status = IsCoolWith.objects.select_for_update().get(requester=target, requestee=user, status=CoolStatus.PENDING)
            except ObjectDoesNotExist:
                raise RelationshipException('Friend request not found')
            cool_status.status = CoolStatus.ACCEPTED
            cool_status.save()
    
    # Logic for cancelling a friend request:
    def cancel_request(self, user, target):
        if are_friends(user, target):
            raise RelationshipException('You are already friends with this user. Need to remove them as a friend instead.')
        with transaction.atomic():
            try:
                cool_status = IsCoolWith.objects.select_for_update().get(requester=user, requestee=target, status=CoolStatus.PENDING)
            except ObjectDoesNotExist:
                raise RelationshipException('Friend request not found')
            cool_status.delete()

    # Logic for rejecting a friend request:
    def reject_request(self, user, target):
        if are_friends(user, target):
            raise RelationshipException('You are already friends with this user. Need to remove them as a friend instead.')
        with transaction.atomic():
            try:
                cool_status = IsCoolWith.objects.select_for_update().get(requester=target, requestee=user, status=CoolStatus.PENDING)
            except ObjectDoesNotExist:
                raise RelationshipException('Friend request not found')
            cool_status.delete()

    # Logic for removing a friend:
    def remove_friend(self, user, target):
        if target.id == 2:
            raise RelationshipException('Computer says no')
        with transaction.atomic():
            cool_status = IsCoolWith.objects.select_for_update().filter(
                (Q(requester=user) & Q(requestee=target)) |
                (Q(requester=target) & Q(requestee=user)),
                status=CoolStatus.ACCEPTED
            )
            if not cool_status:
                raise RelationshipException('You are not friends with this user')
            cool_status.delete()
    
    # Logic for unblocking a user:
    def unblock_user(self, user, target):
        with transaction.atomic():
            try:
                no_cool = NoCoolWith.objects.select_for_update().get(blocker=user, blocked=target)
            except ObjectDoesNotExist:
                raise BlockingException('You have not blocked this user')
            no_cool.delete()

class ListFriendsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        cool_with_entries = IsCoolWith.objects.filter(Q(requester=user) | Q(requestee=user))
        serializer = ListFriendsSerializer(cool_with_entries, many=True, context={'user_id': user.id})
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class UpdateAvatarView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] #TODO CHANGE THIS LATER

    def put(self, request):
        # Check if 'avatar' is in request.FILES
        if 'avatar' not in request.FILES:
            return Response({'error': 'Avatar must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the avatar file from request.FILES
        avatar = request.FILES['avatar']

        # Call the utility function to process the avatar
        result = process_avatar(request.user, avatar)

        # Check if there was an error during processing
        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # Return the success response with the avatar URL
        return Response(result, status=status.HTTP_200_OK)
    
class UpdateUserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
            return Response({'error': 'All fields must be provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if the new username is valid
        # TODO: Wait for issue #108

        # Check if the language is valid
        valid_languages = ['en-US', 'pt-PT', 'pt-BR', 'de-DE', 'uk-UA', 'ne-NP']
        if new_language not in valid_languages:
            return Response({'error': 'Invalid language'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the user info
        user.username = new_username
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.language = new_language

        # Save the user object
        try:
            user.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the success response
        return Response({'success': 'User info updated'}, status=status.HTTP_200_OK)