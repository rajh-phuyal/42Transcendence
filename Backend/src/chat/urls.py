from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CreateConversationView, RenameConversationView, ShowConversationView, SendMessageView, ListConversationsView, LoadConversationsView, LoadConversationView, LoadUnreadMessagesView
from . import views

urlpatterns = [
	path('count/unread/', LoadUnreadMessagesView.as_view(), name='load_unread_messages'),
	path('load/conversations/', LoadConversationsView.as_view(), name='load_conversations'),
	path('load/conversation/<int:conversation_id>/messages/', LoadConversationView.as_view(), name='load_conversation'),


	# Below is old code!
	path('create-conversation/', CreateConversationView.as_view(), name='create_conversation'),
	path('rename-conversation/', RenameConversationView.as_view(), name='rename_conversation'),
    path('show-conversation/', ShowConversationView.as_view(), name='show_conversation'),
    path('send-message/', SendMessageView.as_view(), name='send_message'),
    path('test/', views.test_chat, name='test'),
    path('conversations/', ListConversationsView.as_view(), name='list_conversations'),

	# TODO: REVIEW THE NAMES OF THE ENDPOINTS CHAT -> CONVERSATION
	# Chat listing and deletion
    # path('chats/list/', ListChatsView.as_view(), name='list_chats'),
    # path('chat/delete/', DeleteChatView.as_view(), name='delete_chat'),

    # (Optional) Group chat endpoints
    # path('group-chat/create/', CreateGroupChatView.as_view(), name='create_group_chat'),
    # path('group-chat/add-member/', AddMemberToGroupChatView.as_view(), name='add_member_to_group_chat'),
    # path('group-chat/remove-member/', RemoveMemberFromGroupChatView.as_view(), name='remove_member_from_group_chat'),
]