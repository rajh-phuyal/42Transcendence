from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext as _, activate
from core.response import error_response

# Base view class for all authenticated views we wann create
class BaseAuthenticatedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        # Set the preferred language based on the authenticated user
        if request.user:
            preferred_language = getattr(request.user, 'language', 'en-us')
            activate(preferred_language)
        else:
            # Should never happen due to JWTAuthentication:
            return error_response(_("User not authenticated"), status_code=401)
            
        # Proceed to the view logic
        return super().dispatch(request, *args, **kwargs)