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


class SendFriendRequestView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication!

    # TODO: things to concider:
    # Efficiency: The current code makes multiple queries (e.g., checking for existing friendships, blocked users). You might want to optimize by reducing the number of database queries. For example:
        # Use select_related or prefetch_related to load related objects in one query where necessary.
        # You can refactor your query logic for the IsCoolWith and NoCoolWith relationships by combining the queries into a single Q object for clarity and efficiency.


    def post(self, request):
        requester_id = request.data.get('requester_id')
        requestee_id = request.data.get('requestee_id')
    
        # Check if the requester exists
        try:
            requester = User.objects.get(id=requester_id)
        except User.DoesNotExist:
            return Response({'error': f'User with id {requester_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requestee exists
        try:
            requestee = User.objects.get(id=requestee_id)
        except User.DoesNotExist:
            return Response({'error': f'User with id {requestee_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the requester and requestee are the same user
        if requester_id == requestee_id:
            return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)


        # Get the current cool state between the requester and requestee
        already_cool = IsCoolWith.objects.filter(
            (Q(requester_id=requester_id) & Q(requestee_id=requestee_id)) |
            (Q(requester_id=requestee_id) & Q(requestee_id=requester_id))
        )

        # Check if the requester and requestee are already friends
        # -> Message that the users are already friends
        
        if already_cool.filter(status=CoolStatus.ACCEPTED).exists():
            return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
        elif already_cool.filter(status=CoolStatus.PENDING).exists():
            if already_cool.filter(status=CoolStatus.PENDING).first().requester_id == requester_id:
                # Check if the requester has already sent a friend request to the requestee
                # -> Message be patient, the request is pending
                return Response({'error': 'Friend request is pending'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Check if the requestee has already sent a friend request to the requester
                # -> Accept the friend request
                already_cool.update(status=CoolStatus.ACCEPTED)
                return Response({'success': 'Friend request accepted'}, status=status.HTTP_200_OK)
        elif already_cool.filter(status=CoolStatus.REJECTED).exists():
            if already_cool.filter(status=CoolStatus.REJECTED).first().requester_id == requester_id:
                # Check if the requestee has rejected a previous friend request from the requester
                # -> Message that the requestee has rejected the request
                return Response({'error': 'Friend request was rejected'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Check if the requester has rejected a previous friend request from the requestee
                # -> Update the status to accepted
                already_cool.update(status=CoolStatus.ACCEPTED)
                return Response({'success': 'Friend request accepted'}, status=status.HTTP_200_OK)

        # So there was no previous cool state between the requester and requestee...

        # Check if the requestee has blocked the requester
        # -> Message that the requestee has blocked the requester
        requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id)
        if requestee_blocked.exists():
            return Response({'error': 'You have been blocked by this user'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the requester has blocked the requestee
        # -> Message u need to unblock the user first
        requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id)
        if requester_blocked.exists():
            return Response({'error': 'You have blocked this user, you need to unblock them first'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new friend request
        new_cool = IsCoolWith(requester_id=requester_id, requestee_id=requestee_id)
        new_cool.save()
        # Return a success message
        return Response({'success': 'Friend request sent'}, status=status.HTTP_201_CREATED)
    

class AcceptFriendRequestView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication!

    def post(self, request):
        requester_id = request.data.get('requester_id')
        requestee_id = request.data.get('requestee_id')

        # Check if both requester and requestee IDs are provided
        if not requestee_id or not requester_id:
            return Response({'error': 'Both requester and requestee IDs must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
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

        # TODO: logic for rejecting the friend request

        ''' Do we need this? Doed it make sense to check if the users have blocked each other here? If they're blocked, they cant send a friend request in the first place
          Check if either user has blocked the other
        requester_blocked = NoCoolWith.objects.filter(blocker_id=requester_id, blocked_id=requestee_id).exists()
        requestee_blocked = NoCoolWith.objects.filter(blocker_id=requestee_id, blocked_id=requester_id).exists()

        if requester_blocked or requestee_blocked:
            return Response({'error': 'One of the users has blocked the other'}, status=status.HTTP_400_BAD_REQUEST)
        '''

        # Accept the friend request
        friend_requests.status = CoolStatus.ACCEPTED
        friend_requests.save()
        return Response({'success': 'Friend request accepted'}, status=status.HTTP_200_OK)
    

class RejectFriendRequestView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def post(self, request):
        requestee_id = request.data.get('requestee_id')
        requester_id = request.data.get('requester_id')

        # Check if both requester and requestee IDs are provided
        if not requestee_id or not requester_id:
            return Response({'error': 'Both requester and requestee IDs must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
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
                

class BlockUserView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def post(self, request):
        blocker_id = request.data.get('blocker_id')
        blocked_id = request.data.get('blocked_id')

        # Check if both blocker and blocked IDs are provided
        if not blocker_id or not blocked_id:
            return Response({'error': 'Both blocker and blocked IDs must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if we are trying to block ourselves
        if blocker_id == blocked_id:
            return Response({'error': 'You cannot block yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the block already exists
        block_exists = NoCoolWith.objects.filter(blocker_id=blocker_id, blocked_id=blocked_id).exists()

        if block_exists:
            return Response({'error': 'You have already blocked this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the users are already friends
        friendship = IsCoolWith.objects.filter(
            (Q(requester_id=blocker_id) & Q(requestee_id=blocked_id)) |
            (Q(requester_id=blocked_id) & Q(requestee_id=blocker_id)),
            status=CoolStatus.ACCEPTED
        )

        # If they are friends, delete the friendship
        if friendship.exists():
            friendship.delete()

        new_block = NoCoolWith(blocker_id=blocker_id, blocked_id=blocked_id)
        new_block.save()

        return Response({'success': 'User blocked'}, status=status.HTTP_200_OK)


class UnblockUserView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication

    def post(self, request):
        blocker_id = request.data.get('blocker_id')
        blocked_id = request.data.get('blocked_id')

        # Check if both blocker and blocked IDs are provided
        if not blocker_id or not blocked_id:
            return Response({'error': 'Both blocker and blocked IDs must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Chech if we are trying to unblock ourselves
        if blocker_id == blocked_id:
            return Response({'error': 'You cannot unblock yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the block exists
        block = NoCoolWith.objects.filter(blocker_id=blocker_id, blocked_id=blocked_id)

        if not block.exists():
            return Response({'error': 'You have not blocked this user'}, status=status.HTTP_400_BAD_REQUEST)
        
        block.delete()

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
    