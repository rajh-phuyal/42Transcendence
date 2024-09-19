from rest_framework.permissions import AllowAny  # Import AllowAny #TODO: remove line
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import User, CoolStatus, IsCoolWith, NoCoolWith
from .serializers import UserSerializer

# ProfileView for retrieving a single user's profile by ID
class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'  # This tells Django to look up the user by the 'id' field
    permission_classes = [AllowAny]  # This allows anyone to access this view #TODO: implement the token-based authentication!


class FriendRequestView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication!

    def post(self, request):
        action = request.data.get('action')

        if not action or action not in ['send', 'accept', 'reject', 'cancel']:
            return Response({'error': 'Valid action must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        requester_id = request.data.get('requester_id')
        requestee_id = request.data.get('requestee_id')

        # Check if requester exists
        try:
            requester = User.objects.get(id=requester_id)
        except User.DoesNotExist: #TODO: remove Key "requester_id" after development 
            return Response({'error': f'Key --> requester_id.     Requester with id {requester_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if requestee exists
        try:
            requestee = User.objects.get(id=requestee_id)
        except User.DoesNotExist:
            return Response({'error': f'Key --> requestee_id.     Requestee with id {requestee_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requester and requestee are the same user
        if requester_id == requestee_id:
            return Response({'error': f'Key --> {action}.    Requester and requestee cannot be the same user'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requestee has blocked the requester
        requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id)
        if requestee_blocked.exists():
            return Response({'error': 'You have been blocked by this user'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requester has blocked the requestee
        requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id)
        if requester_blocked.exists():
            return Response({'error': 'You have blocked this user, you need to unblock them first'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'send':
            return self.send_friend_request(request, requester_id, requestee_id)
        elif action == 'accept':
            return self.accept_friend_request(request, requester_id, requestee_id)
        elif action == 'reject':
            return self.reject_friend_request(request, requester_id, requestee_id)
        elif action == 'cancel':
            return self.cancel_friend_request(request, requester_id, requestee_id)
        
    
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
            friend_requests = IsCoolWith.objects.get(
                requester_id=requester_id,
                requestee_id=requestee_id
            )
        except IsCoolWith.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
    
        # TODO: verify if the requester is the requestee, when we have authentication implemented

        # Check if the friend request is already accepted
        if friend_requests.status == CoolStatus.ACCEPTED:
            return Response({'error': 'Friend request has already been accepted'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if status is pending
        if friend_requests.status != CoolStatus.PENDING:
            return Response({'error': 'Friend request is not pending'}, status=status.HTTP_400_BAD_REQUEST)

        # Accept the friend request
        friend_requests.status = CoolStatus.ACCEPTED
        friend_requests.save()
        return Response({'success': 'Friend request accepted'}, status=status.HTTP_200_OK)


    def reject_friend_request(self, request, requester_id, requestee_id):
        
        # Check if the friend request exists
        try:
            friend_requests = IsCoolWith.objects.get(
                requester_id=requester_id,
                requestee_id=requestee_id
            )
        except IsCoolWith.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the users are already friends
        if friend_requests.status == CoolStatus.ACCEPTED:
            return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the friend request is already rejected
        if friend_requests.status == CoolStatus.REJECTED:
            return Response({'error': 'Friend request has already been rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the friend request is pending
        if friend_requests.status != CoolStatus.PENDING:
            return Response({'error': 'Friend request is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reject the friend request
        friend_requests.status = CoolStatus.REJECTED
        friend_requests.save()
        return Response({'success': 'Friend request rejected'}, status=status.HTTP_200_OK)
    

    def cancel_friend_request(self, request, requester_id, requestee_id):
        
        # Check if the friend request exists
        friend_requests = IsCoolWith.objects.filter(
            requester_id=requester_id,
            requestee_id=requestee_id,
            status=CoolStatus.PENDING
        ).first()

        if not friend_requests:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        friend_requests.delete()

        return Response({'success': 'Friend request cancelled'}, status=status.HTTP_200_OK)


class ListFriendsView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def get(self, request):
        user_id = request.query_params.get('user_id')

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

    def put(self, request):
        action = request.data.get('action')

        if not action or action not in ['block', 'unblock']:
            return Response({'error': 'Key --> "block" or "unblock".     Valid action must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        blocker_id = request.data.get('blocker_id')
        blocked_id = request.data.get('blocked_id')

        if not blocker_id:
            return Response({'error': 'Key --> "blocker_id".     Blocker ID must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not blocked_id:
            return Response({'error': 'Key --> "blocked_id".     Blocked ID must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        if blocker_id == blocked_id:
            return Response({'error': f'You cannot {action} yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'block':
            return self.block_user(request, blocker_id, blocked_id)
        elif action == 'unblock':
            return self.unblock_user(request, blocker_id, blocked_id)
        

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


    
class RemoveFriendView(APIView): 
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def post(self, request):
        user_id = request.data.get('user_id')
        friend_id = request.data.get('friend_id')

        # Check if both user and friend IDs are provided
        if not user_id or not friend_id:
            return Response({'error': 'Both user and friend IDs must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        friendship = IsCoolWith.objects.filter(
            (Q(requester_id=user_id) & Q(requestee_id=friend_id)) |
            (Q(requester_id=friend_id) & Q(requestee_id=user_id)),
            status=CoolStatus.ACCEPTED
        )

        if not friendship.exists():
            return Response({'error': 'You are not friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        friendship.delete()

        return Response({'success': 'Friend removed'}, status=status.HTTP_200_OK)
    