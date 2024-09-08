from rest_framework import generics, status # type: ignore
from rest_framework import exceptions # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny # type: ignore
from rest_framework.views import exception_handler # type: ignore
from rest_framework import exceptions # type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView # type: ignore
from .serializers import InternalTokenObtainPairSerializer

class InternalTokenObtainPairView(TokenObtainPairView):
    serializer_class = InternalTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        self.response_data = {
            "message": "Registration successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "userId": user.id,
            "username": user.username,
        }

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(self.response_data, status=status.HTTP_201_CREATED)

    def handle_exception(self, exc):
        response = exception_handler(exc, self.get_exception_handler_context())

        if response is not None:
            if isinstance(exc, exceptions.ValidationError):
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