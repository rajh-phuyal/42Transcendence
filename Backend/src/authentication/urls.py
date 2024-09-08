from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView  # type: ignore
from .views import RegisterView, InternalTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', InternalTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]