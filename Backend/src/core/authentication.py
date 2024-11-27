from rest_framework.views import APIView
from core.cookies import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.exceptions import NotAuthenticated
import logging


# Base view class for all authenticated views we wanna create
class BaseAuthenticatedView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)

        # Let the authentication process complete first, or we will have a 500 (which is BAD!)
        self.perform_authentication(request)

        # we can safely check the authentication status # TODO: currently this throws a 500, needs fix
        if isinstance(request.user, AnonymousUser):
            raise NotAuthenticated(_("User is not authenticated"))

        preferred_language = getattr(request.user, 'language', 'en-US')
        activate(preferred_language)
        logging.info(f"User {request.user} has preferred language {preferred_language}")

        return request