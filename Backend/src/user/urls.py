from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProfileView

urlpatterns = [
	path('profile/<int:id>/', ProfileView.as_view(), name='profile'),
]