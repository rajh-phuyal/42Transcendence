from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CreateChatView, RenameChatView, ShowChatView, SendMessageView

urlpatterns = [
	path('create-chat/', CreateChatView.as_view(), name='create_chat'),
	path('rename-chat/', RenameChatView.as_view(), name='rename_chat'),
    path('show-chat/', ShowChatView.as_view(), name='show_chat'),
    path('send-message/', SendMessageView.as_view(), name='send_message'),

	# TODO:
	# Chat listing and deletion
    # path('chats/list/', ListChatsView.as_view(), name='list_chats'),
    # path('chat/delete/', DeleteChatView.as_view(), name='delete_chat'),

    # (Optional) Group chat endpoints
    # path('group-chat/create/', CreateGroupChatView.as_view(), name='create_group_chat'),
    # path('group-chat/add-member/', AddMemberToGroupChatView.as_view(), name='add_member_to_group_chat'),
    # path('group-chat/remove-member/', RemoveMemberFromGroupChatView.as_view(), name='remove_member_from_group_chat'),
]