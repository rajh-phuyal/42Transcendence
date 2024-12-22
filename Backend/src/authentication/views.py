from rest_framework import generics, exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.serializers import RegisterSerializer, InternalTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.cookies import set_jwt_cookies, unset_jwt_cookies
from core.authentication import BaseAuthenticatedView
from authentication.models import DevUserData
from core.response import success_response, error_response
from django.utils.translation import gettext as _, activate
from core.decorators import barely_handle_exceptions
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # No authentication required for registration

    @barely_handle_exceptions
    def post(self, request, *args, **kwargs):
        # Activate language from query params or fallback to default
        preferred_language = request.query_params.get('language', 'en-us')
        activate(preferred_language)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
            user.language = preferred_language
            user.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Store dev user data if needed
            DevUserData.objects.update_or_create(
                user=user,
                defaults={
                    'username': user.username,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            )

            response = success_response(_("User registered successfully"), **{
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

        except Exception as e:
            raise exceptions.APIException(f"Error during user registration: {str(e)}")

    def get(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def put(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def delete(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def patch(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def head(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def options(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def trace(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

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
                return error_response(_("User not found"))

            custom_response = success_response(_("User logged in successfully"), **{
                "userId": user.id,
                "username": user.username,
                "language": user.language,
            })

            set_jwt_cookies(
                response=custom_response,
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
            return custom_response
        return error_response(_("Login failed"))

    def get(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def put(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def delete(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def patch(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def head(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def options(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def trace(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

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

class TokenVerifyView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        # Just need to pass through the auth check with cookies
        return success_response(_("Token is valid"), **{
            'userId': request.user.id,
            'username': request.user.username,
            'isAuthenticated': True
        })

class InternalTokenRefreshView(TokenRefreshView):
    @barely_handle_exceptions
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie instead of request body
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT_COOKIE['REFRESH_COOKIE_NAME'])
        if not refresh_token:
            return error_response(_('No refresh token found in cookies'))

        # Add refresh token to request data
        request.data['refresh'] = refresh_token

        # Call parent class post method
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            custom_response = success_response(_("Token refreshed successfully"))

            # Set new tokens in cookies
            return set_jwt_cookies(
                response=custom_response,
                access_token=response.data['access'],
                refresh_token=response.data['refresh']
            )

        return response

    def get(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def put(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def delete(self, request):
        return error_response(_("Method not allowed"), status_code=405)

    def patch(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def head(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def options(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def trace(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)
