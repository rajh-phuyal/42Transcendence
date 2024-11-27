from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.exceptions import NotAuthenticated
import logging

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT_COOKIE['ACCESS_COOKIE_NAME'])

        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

# Base view class for all authenticated views we wanna create
class BaseAuthenticatedView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)

        # Activate the preferred language if the user is authenticated
        if not isinstance(request.user, AnonymousUser):
            preferred_language = getattr(request.user, 'language', 'en-US')  # Fallback to 'en-US'
            activate(preferred_language)
            logging.info(f"User {request.user} has preferred language {preferred_language}")
        else:
            raise NotAuthenticated(_("User is not authenticated"))
        return request