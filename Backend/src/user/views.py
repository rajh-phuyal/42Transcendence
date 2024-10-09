from rest_framework.permissions import AllowAny  # Import AllowAny #TODO: remove line
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import User, CoolStatus, IsCoolWith, NoCoolWith
from .serializers import UserSerializer
from .utils import get_and_validate_data
from .exceptions import ValidationException

# ProfileView for retrieving a single user's profile by ID
class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'  # This tells Django to look up the user by the 'id' field
    permission_classes = [AllowAny]  # This allows anyone to access this view #TODO: implement the token-based authentication!
    
    def get(self, request, id):
        try:
            user = self.queryset.get(id=id)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    ''' TODO: add more fields like
    * friends list count
    * user points
    * match history
    * etc.
    '''


class FriendRequestView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication!

    def put(self, request):
        action = request.data.get('action')

        if not action or action not in ['accept', 'reject']:
            return Response({'error': 'Invalid action. PUT valid actions are "accept" and "reject"'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            requester_id, requestee_id = get_and_validate_data(request, action, 'requester_id', 'requestee_id')
       
            # Check if the requestee has blocked the requester
            requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id)
            if requestee_blocked.exists():
                return Response({'error': 'You have been blocked by this user'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the requester has blocked the requestee
            requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id)
            if requester_blocked.exists():
                return Response({'error': 'You have blocked this user, you need to unblock them first'}, status=status.HTTP_400_BAD_REQUEST)

            if action == 'accept':
                return self.accept_friend_request(request, requester_id, requestee_id)
            return self.reject_friend_request(request, requester_id, requestee_id)
        
        except ValidationException as e:
            return Response(e.detail, status=e.status_code)
        
    
    def post(self, request):
        action = request.data.get('action')

        if not action or action not in ['send']:
            return Response({'error': 'Invalid action. POST valid action is "send"'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            requester_id, requestee_id = get_and_validate_data(request, action, 'requester_id', 'requestee_id')
            
            # Check if the requestee has blocked the requester
            requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id)
            if requestee_blocked.exists():
                return Response({'error': 'You have been blocked by this user'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the requester has blocked the requestee
            requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id)
            if requester_blocked.exists():
                return Response({'error': 'You have blocked this user, you need to unblock them first'}, status=status.HTTP_400_BAD_REQUEST)
            
            return self.send_friend_request(request, requester_id, requestee_id)
        
        except ValidationException as e:
            return Response(e.detail, status=e.status_code)


    def delete(self, request):
        action = request.data.get('action')

        try:
            if not action or action not in ['cancel']:
                return Response({'error': 'Invalid action. DELETE valid action is "cancel"'}, status=status.HTTP_400_BAD_REQUEST)
            
            requester_id, requestee_id = get_and_validate_data(request, action, 'requester_id', 'requestee_id')
            if not requester_id:
                return requestee_id
            
            return self.cancel_friend_request(request, requester_id, requestee_id)

        except ValidationException as e:
            return Response(e.detail, status=e.status_code)


    def send_friend_request(self, request, requester_id, requestee_id):
    
        # Get the current cool state between the requester and requestee
        already_cool = IsCoolWith.objects.filter(
            (Q(requester_id=requester_id) & Q(requestee_id=requestee_id)) |
            (Q(requester_id=requestee_id) & Q(requestee_id=requester_id))
        )

        # Check if the users are already friends
        if already_cool.filter(status=CoolStatus.ACCEPTED).exists():
            return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        
         # Check if the friend request is pending
        if already_cool.filter(status=CoolStatus.PENDING).exists():
            return Response({'error': 'Friend request is already pending'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the friend request was previously rejected
        if already_cool.filter(status=CoolStatus.REJECTED).exists():
            return Response({'error': 'Friend request was rejected'}, status=status.HTTP_400_BAD_REQUEST)

        # If there was no previous cool state between the requester and requestee...

        # Create a new friend request
        new_cool = IsCoolWith(requester_id=requester_id, requestee_id=requestee_id)
        new_cool.save()
        # Return a success message
        return Response({'success': 'Friend request sent'}, status=status.HTTP_201_CREATED)


    def accept_friend_request(self, request, requester_id, requestee_id):

        # Check if the friend request exists
        try:
            friend_request = IsCoolWith.objects.get(
                requester_id=requester_id,
                requestee_id=requestee_id
            )
        except IsCoolWith.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
    
        # TODO: verify if the requester is the requestee, when we have authentication implemented

        # Check if the friend request is already accepted
        if friend_request.status == CoolStatus.ACCEPTED:
            return Response({'error': 'Friend request has already been accepted'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if status is pending
        if friend_request.status != CoolStatus.PENDING and friend_request.status != CoolStatus.REJECTED:
            return Response({'error': 'Friend request is not pending or rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Accept the friend request
        friend_request.status = CoolStatus.ACCEPTED
        friend_request.save()
        return Response({'success': 'Friend request accepted'}, status=status.HTTP_200_OK)


    def reject_friend_request(self, request, requester_id, requestee_id):
        
        # Check if the friend request exists
        try:
            friend_request = IsCoolWith.objects.get(
                requester_id=requester_id,
                requestee_id=requestee_id
            )
        except IsCoolWith.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the users are already friends
        if friend_request.status == CoolStatus.ACCEPTED:
            return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the friend request is already rejected
        if friend_request.status == CoolStatus.REJECTED:
            return Response({'error': 'Friend request has already been rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the friend request is pending
        if friend_request.status != CoolStatus.PENDING:
            return Response({'error': 'Friend request is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reject the friend request
        friend_request.status = CoolStatus.REJECTED
        friend_request.save()
        return Response({'success': 'Friend request rejected'}, status=status.HTTP_200_OK)
    

    def cancel_friend_request(self, request, requester_id, requestee_id):
        
        # Check if the friend request exists
        friend_request = IsCoolWith.objects.filter(
            requester_id=requester_id,
            requestee_id=requestee_id,
            status=CoolStatus.PENDING
        ).first()

        if not friend_request:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        friend_request.delete()

        return Response({'success': 'Friend request cancelled'}, status=status.HTTP_200_OK)


class ListFriendsView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def get(self, request,id):
        user_id = id

        if not user_id:
            return Response({'error': 'User ID must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        friendships = IsCoolWith.objects.filter(
           (Q(requester_id=user_id) | Q(requestee_id=user_id)) & Q(status=CoolStatus.ACCEPTED)
        )

        friends_list = []

        for friendship in friendships:
            if friendship.requester_id == int(user_id):
                friend = friendship.requestee
            else:
                friend = friendship.requester
        
            friends_list.append({
                'id': friend.id,
                'username': friend.username,
            })

        return Response({'friends': friends_list}, status=status.HTTP_200_OK)
                

class ModifyFriendshipView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def post(self, request):
        action = request.data.get('action')
        if not action or action not in ['remove', 'block']:
            return Response({'error': 'Invalid action. PUT valid actions are "remove" and "block"'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # NOTE: inside of this method it makes sense to name the variables requester_id and requestee_id rather than blocker_id and blocked_id
            requester_id, requestee_id = get_and_validate_data(request, action, 'blocker_id', 'blocked_id')
            if not requester_id:
                return requestee_id
            
            if action == 'block':
                return self.block_user(request, requester_id, requestee_id)
            return self.remove_friend(request, requester_id, requestee_id)
        
        except ValidationException as e:
            return Response(e.detail, status=e.status_code)


    def delete(self, request):
        action = request.data.get('action')
        if not action or action not in ['unblock']:
            return Response({'error': 'Invalid action. DELETE valid action is "unblock"'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blocker_id, blocked_id = get_and_validate_data(request, action, 'blocker_id', 'blocked_id')
            if not blocker_id:
                return blocked_id
            
            return self.unblock_user(request, blocker_id, blocked_id)
        
        except ValidationException as e:
            return Response(e.detail, status=e.status_code)
        

    def block_user(self, request, blocker_id, blocked_id):
        # Check if the block already exists
        block_exists = NoCoolWith.objects.filter(blocker_id=blocker_id, blocked_id=blocked_id).exists()

        if block_exists:
            return Response({'error': 'You have already blocked this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        NoCoolWith.objects.create(blocker_id=blocker_id, blocked_id=blocked_id)

        return Response({'success': 'User blocked'}, status=status.HTTP_200_OK)
    
    def unblock_user(self, request, blocker_id, blocked_id):
        # Check if the block exists
        block = NoCoolWith.objects.filter(blocker_id=blocker_id, blocked_id=blocked_id).first()

        if not block:
            return Response({'error': 'You have not blocked this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        block.delete()

        # The users go back to their friendship state
        # No need to recreate the friendship in is_cool_with if it already exists
        return Response({'success': 'User unblocked'}, status=status.HTTP_200_OK)

    def remove_friend(self, request, blocker_id, blocked_id):
        friendship = IsCoolWith.objects.filter(
            (Q(requester_id=blocker_id) & Q(requestee_id=blocked_id)) |
            (Q(requester_id=blocked_id) & Q(requestee_id=blocker_id)),
            status=CoolStatus.ACCEPTED
        )

        if not friendship.exists():
            return Response({'error': 'You are not friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        friendship.delete()

        return Response({'success': 'Friend removed'}, status=status.HTTP_200_OK)
