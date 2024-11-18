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

    # TODO: main branch was fucked, so I commented this...
    # 
    # def perform_create(self, serializer):
    #     try:
    #         user = serializer.save()
    #         refresh = RefreshToken.for_user(user)
    #         DevUserData.objects.update_or_create(
    #             user=user,
    #             defaults={
    #                 'username': user.username,
    #                 'access_token': str(refresh.access_token),
    #                 'refresh_token': str(refresh),
    #             }
    #         )
    #     except Exception as e:
    #         raise exceptions.APIException(f"Error during user registration: {str(e)}")

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

    def handle_exception(self, exc):
        if isinstance(exc, BarelyAnException):
            return error_response(exc.detail, status_code=exc.status_code)
    
        # Fall back to the default exception handler
        response = exception_handler(exc, self.get_exception_handler_context())
        err_msg = _("Error during user registration: {error}").format(error=str(exc))

        if response is not None:
            if isinstance(exc, exceptions.ValidationError):
                return error_response(err_msg, status_code=status.HTTP_400_BAD_REQUEST)
            elif isinstance(exc, exceptions.AuthenticationFailed):
                return error_response(err_msg, status_code=status.HTTP_401_UNAUTHORIZED)
            elif isinstance(exc, exceptions.NotAuthenticated):
                return error_response(err_msg, status_code=status.HTTP_401_UNAUTHORIZED)
            elif isinstance(exc, exceptions.PermissionDenied):
                return error_response(err_msg, status_code=status.HTTP_403_FORBIDDEN)
            elif isinstance(exc, exceptions.NotFound):
                return error_response(err_msg, status_code=status.HTTP_404_NOT_FOUND)
            return error_response(err_msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        return error_response(err_msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   

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
            # TODO: Main branch was fucked so i commented this...
            # DevUserData.objects.update_or_create(
            #     user=user,
            #     defaults={
            #         'access_token': access_token,
            #         'refresh_token': refresh_token,
            #     }
            #)
        
        return response

    def get_user_from_request(self, request):
        """
        Utility function to get the authenticated user from the request.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.user
