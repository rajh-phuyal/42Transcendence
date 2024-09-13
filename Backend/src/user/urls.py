from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProfileView

urlpatterns = [
	path('profile/<int:id>/', ProfileView.as_view(), name='profile'),

	# TODO iplement those endpoints:
	# Friend request system
#    path('friend-request/send/', SendFriendRequestView.as_view(), name='send_friend_request'),
#    path('friend-request/accept/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
#    path('friend-request/decline/', DeclineFriendRequestView.as_view(), name='decline_friend_request'),
#    path('friends/list/', ListFriendsView.as_view(), name='list_friends'),

    # Blocking/unblocking users
#    path('friends/block/', BlockUserView.as_view(), name='block_user'),
#    path('friends/unblock/', UnblockUserView.as_view(), name='unblock_user'),
]