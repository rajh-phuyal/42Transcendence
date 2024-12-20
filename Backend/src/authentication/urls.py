from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.views import (
    RegisterView,
    InternalTokenObtainPairView,
    TokenVerifyView,
    LogoutView,
    InternalTokenRefreshView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', InternalTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', InternalTokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
]