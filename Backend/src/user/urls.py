from django.urls import path
from .views import (
    ProfileView,
    FriendRequestView,
    ModifyFriendshipView,
    ListFriendsView,
    # TODO: REMOVE after development
    ListTokensView
)

urlpatterns = [
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),

	# Friend requesting
    path('friend-request/', FriendRequestView.as_view(), name='friend_request'),
    path('friend/list/<int:id>/', ListFriendsView.as_view(), name='list_friends'),

    # Blocking/unblocking users / removing friends
    path('modify-friendship/', ModifyFriendshipView.as_view(), name='modify_friendship'),

    # TODO: REMOVE after development. this is very insecure, but useful for development
    path('list-tokens/', ListTokensView.as_view(), name='list_tokens'),
]