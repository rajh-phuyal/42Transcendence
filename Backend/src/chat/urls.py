from django.urls import path
from chat.views import LoadConversationsView, LoadConversationView, CreateConversationView

urlpatterns = [
	path('create/conversation/', CreateConversationView.as_view(), name='create_conversation'),
	path('load/conversations/', LoadConversationsView.as_view(), name='load_conversations'),
	path('load/conversation/<int:conversation_id>/messages/', LoadConversationView.as_view(), name='load_conversation'),
]