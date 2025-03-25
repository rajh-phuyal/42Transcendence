from django.utils import timezone
from rest_framework.views import APIView
from core.cookies import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.response import error_response
from core.exceptions import NotAuthenticated
from rest_framework import status
import logging
from core.constants import BOLD, RESET, COLORS


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

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        return request

    # For my custom logging
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user = request.user
        if user:
            user_color = self.get_user_color_for_logs(user.id)
        else:
            user_color = RESET
        time_str = timezone.now().strftime("%H:%M")
        user_display = f"{user}"
        aligned_user = user_display.ljust(20)
        logging.info(f">> {BOLD}{time_str}\t {user_color}{aligned_user}{RESET}{request.method} {request.path}{RESET}")
        return response

    # Each user gets a different color for logs - so not MVP :D
    def get_user_color_for_logs(self, userid):
        if not userid:
            return RESET
        return COLORS[userid % len(COLORS)]

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
