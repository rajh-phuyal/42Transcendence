from rest_framework.views import APIView
from core.cookies import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.response import error_response
from core.exceptions import NotAuthenticated
from rest_framework import status
import logging


# Base view class for all authenticated views we wanna create
class BaseAuthenticatedView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_authentication(self, request):
        super().perform_authentication(request)

        # Set language after authentication
        preferred_language = getattr(request.user, 'language', 'en-US')
        activate(preferred_language)

        # Check for anonymous user and return formatted error response
        if isinstance(request.user, AnonymousUser):
            raise NotAuthenticated(_("User is not authenticated"), status_code=status.HTTP_401_UNAUTHORIZED)

        logging.info(f"User {request.user} has preferred language {preferred_language}")

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        return request

    # We don't want to allow any methods by default
    # If a child class wants to allow a method it has to overwrite it
    def post(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def head(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def options(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def trace(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
