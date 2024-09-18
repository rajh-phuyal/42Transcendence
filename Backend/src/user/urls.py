from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ProfileView,
    FriendRequestView,
    BlockUserView,
    UnblockUserView,
    ListFriendsView,
    RemoveFriendView
)

urlpatterns = [
	path('profile/<int:id>/', ProfileView.as_view(), name='profile'),

	# Friend requesting
    path('friend-request/', FriendRequestView.as_view(), name='friend_request'),
    path('friends/list/', ListFriendsView.as_view(), name='list_friends'),

    # Blocking/unblocking users
    path('block/', BlockUserView.as_view(), name='block_user'),
    path('unblock/', UnblockUserView.as_view(), name='unblock_user'),

    # Remove friend
    path('friends/remove/', RemoveFriendView.as_view(), name='remove_friend'),
]