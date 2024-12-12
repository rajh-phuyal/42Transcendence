from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _, activate
from core.response import error_response
from core.exceptions import NotAuthenticated
import logging

# Base view class for all authenticated views we wanna create
class BaseAuthenticatedView(APIView):
    authentication_classes = [JWTAuthentication]
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