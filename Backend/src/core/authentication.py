from rest_framework.views import APIView
from core.cookies import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.exceptions import BarelyAnException
from core.response import error_response
import logging


class NotAuthenticated(BarelyAnException):
    status_code = 401
    default_detail = _("Authentication credentials were not provided.")

    def __init__(self, detail, status_code=401):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = {
            "status": "error",
            "statusCode": self.status_code,
            "message": detail
        }


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
