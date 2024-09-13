from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView

urlpatterns = [
	path('create-chat/', CreateChatView.as_view(), name='create_chat'),
    path('send-message/<int:chat_id>/', SendMessageView.as_view(), name='send_message'),
]