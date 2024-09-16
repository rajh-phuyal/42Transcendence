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