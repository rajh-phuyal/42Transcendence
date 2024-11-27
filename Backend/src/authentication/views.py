from rest_framework import generics, status
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers import RegisterSerializer, InternalTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import set_jwt_cookies, unset_jwt_cookies
from rest_framework.permissions import IsAuthenticated
from core.authentication import CookieJWTAuthentication
from authentication.models import DevUserData
from core.response import success_response
from django.utils.translation import gettext as _, activate
from core.decorators import barely_handle_exceptions


class RegisterView(APIView):
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
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "userId": user.id,
            "username": user.username,
            "language": user.language,
        })

        # Set the cookies
        return set_jwt_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token
        )

class InternalTokenObtainPairView(TokenObtainPairView):
    serializer_class = InternalTokenObtainPairSerializer

    @barely_handle_exceptions
    def post(self, request, *args, **kwargs):
        # Activate language from query params or fallback to default
        # use like: /login/?language=en-us
        preferred_language = request.query_params.get('language', 'en-us')
        activate(preferred_language)

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = self.get_user_from_request(request)
            user.language = preferred_language

            if not user:
                raise exceptions.AuthenticationFailed(_("User not found"))

            set_jwt_cookies(
                response=response,
                access_token=response.data['access'],
                refresh_token=response.data['refresh']
            )

            DevUserData.objects.update_or_create(
                user=user,
                defaults={
                    'access_token': response.data['access'],
                    'refresh_token': response.data['refresh'],
                }
            )

            # Remove tokens from response data as they're now in cookies
            response.data.pop('access', None)
            response.data.pop('refresh', None)

        return response

    def get_user_from_request(self, request):
        """
        Utility function to get the authenticated user from the request.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.user


class LogoutView(APIView):
    def post(self, request):
        return unset_jwt_cookies(success_response(_("Successfully logged out")))

class TokenVerifyView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(_("Token is valid"), **{
            'userId': request.user.id,
            'username': request.user.username,
            'isAuthenticated': True
        })
