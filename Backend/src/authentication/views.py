from rest_framework.permissions import AllowAny
from rest_framework import generics, serializers, exceptions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def handle_exception(self, exc):
        response = exception_handler(exc, self.get_exception_handler_context())
        if response is not None:
            if isinstance(exc, serializers.ValidationError):
                response.data = {'errors': response.data}
                response.status_code = status.HTTP_400_BAD_REQUEST
            elif isinstance(exc, exceptions.AuthenticationFailed):
                response.data = {'detail': 'Authentication failed'}
                response.status_code = status.HTTP_401_UNAUTHORIZED
            elif isinstance(exc, exceptions.NotAuthenticated):
                response.data = {'detail': 'Not authenticated'}
                response.status_code = status.HTTP_401_UNAUTHORIZED
            elif isinstance(exc, exceptions.PermissionDenied):
                response.data = {'detail': 'Permission denied'}
                response.status_code = status.HTTP_403_FORBIDDEN
            elif isinstance(exc, exceptions.NotFound):
                response.data = {'detail': 'Not found'}
                response.status_code = status.HTTP_404_NOT_FOUND
            else:
                response.data = {'detail': str(exc)}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return response
