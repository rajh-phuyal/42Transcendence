from rest_framework.permissions import AllowAny  # Import AllowAny #TODO: remove line
from rest_framework import generics
from .models import User
from .serializers import UserSerializer

# ProfileView for retrieving a single user's profile by ID
class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'  # This tells Django to look up the user by the 'id' field
    permission_classes = [AllowAny]  # This allows anyone to access this view #TODO: implement the token-based authentication!
