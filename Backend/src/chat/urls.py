from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CreateChatView, RenameChatView, SendMessageView

urlpatterns = [
	path('create-chat/', CreateChatView.as_view(), name='create_chat'),
	path('rename-chat/', RenameChatView.as_view(), name='rename_chat'),
    path('send-message/', SendMessageView.as_view(), name='send_message'),
]