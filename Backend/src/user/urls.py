from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ProfileView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    BlockUserView
)

urlpatterns = [
	path('profile/<int:id>/', ProfileView.as_view(), name='profile'),

    path('friend-request/send/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/accept/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('friend-request/reject/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
	# TODO iplement those endpoints:
	# Friend request system
#    path('friends/list/', ListFriendsView.as_view(), name='list_friends'),

    # Blocking/unblocking users
    path('friends/block/', BlockUserView.as_view(), name='block_user'),
#    path('friends/unblock/', UnblockUserView.as_view(), name='unblock_user'),
]