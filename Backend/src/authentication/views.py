from rest_framework import generics, status
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers import RegisterSerializer, InternalTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import exception_handler
from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.models import DevUserData
from core.response import success_response, error_response
from django.utils.translation import gettext as _, activate
from core.exceptions import BarelyAnException
from core.decorators import barely_handle_exceptions


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        try:
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            DevUserData.objects.update_or_create(
                user=user,
                defaults={
                    'username': user.username,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }
            )
        except Exception as e:
            raise exceptions.APIException(f"Error during user registration: {str(e)}")

    @barely_handle_exceptions
    def create(self, request, *args, **kwargs):
        # Activate language from query params or fallback to default
        # use like: /register/?language=en-us
        preferred_language = request.query_params.get('language', 'en-us')
        activate(preferred_language)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        user = serializer.instance
        user.language = preferred_language
        refresh = RefreshToken.for_user(user)

        response_data = {
            "userId": user.id,
            "username": user.username,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "language": user.language,
        }
        return success_response(_("Welcome on board {username}!").format(username=user.username), status_code=status.HTTP_201_CREATED, **response_data)

class InternalTokenObtainPairView(TokenObtainPairView):
    serializer_class = InternalTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Activate language from query params or fallback to default
        # use like: /login/?language=en-us
        preferred_language = request.query_params.get('language', 'en-us')
        activate(preferred_language)
        
        response = super().post(request, *args, **kwargs)
        user = self.get_user_from_request(request)
        user.language = preferred_language
        
        if user:
            # Get the tokens from the response data
            refresh_token = response.data.get('refresh')
            access_token = response.data.get('access')
            # Store the tokens in the DevUserData table
            DevUserData.objects.update_or_create(
                user=user,
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            )
        
        return response

    def get_user_from_request(self, request):
        """
        Utility function to get the authenticated user from the request.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.user
