from rest_framework.views import APIView
from core.cookies import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.response import error_response
from core.exceptions import NotAuthenticated
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
            raise NotAuthenticated(_("User is not authenticated"), status_code=401)

        logging.info(f"User {request.user} has preferred language {preferred_language}")

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        return request

    # We don't want to allow any methods by default
    # If a child class wants to allow a method it has to overwrite it
    def post(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def put(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def get(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def delete(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def patch(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def head(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def options(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)

    def trace(self, request, *args, **kwargs):
        return error_response(_("Method not allowed"), status_code=405)
