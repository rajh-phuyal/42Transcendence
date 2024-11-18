from rest_framework import generics, status
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import exception_handler
from rest_framework import exceptions
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import InternalTokenObtainPairSerializer
from .models import DevUserData

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


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except exceptions.APIException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.instance
        refresh = RefreshToken.for_user(user)

        response_data = {
            "message": "Registration successful",
            "userId": user.id,
            "username": user.username,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


    def handle_exception(self, exc):
        response = exception_handler(exc, self.get_exception_handler_context())

        if response is not None:
            if isinstance(exc, exceptions.ValidationError):
                response.data = {'errors': response.data}
                response.status_code = status.HTTP_400_BAD_REQUEST
            elif isinstance(exc, exceptions.AuthenticationFailed):
                response.data = {'detail': 'Authentication failed'}
                response.status_code = status.HTTP_401_UNAUTHORIZED
            elif isinstance(exc, exceptions.NotAuthenticated):
                response.data = {'detail': 'Not authenticated'}
                response.status_code = status.HTTP_401_UNAUTHORIZED
            elif isinstance(exc, exceptions.PermissionDenied):
                response.data = {'detail': 'Permission denied'}
                response.status_code = status.HTTP_403_FORBIDDEN
            elif isinstance(exc, exceptions.NotFound):
                response.data = {'detail': 'Not found'}
                response.status_code = status.HTTP_404_NOT_FOUND
            else:
                response.data = {'detail': str(exc)}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return response

        return response


class InternalTokenObtainPairView(TokenObtainPairView):
    serializer_class = InternalTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.get_user_from_request(request)
        
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
