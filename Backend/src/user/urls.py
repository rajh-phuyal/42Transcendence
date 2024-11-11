from django.urls import path
from .views import (
    ProfileView,
    FriendRequestView,
    ModifyFriendshipView,
    ListFriendsView,
    UpdateAvatarView,
    UpdateUserInfoView,
	RelationshipView
)

#   METHOD    | ENDPOINT                | ACTION    | ARGUMENTS   | USE CASE
#-------------|-------------------------|-----------|-------------|-----------------------------------------
#   POST      | /api/user/relationship/ | 'send'    | 'target_id' | Send a friend request
#   POST      | /api/user/relationship/ | 'block'   | 'target_id' | Block a user
#
#   PUT       | /api/user/relationship/ | 'accept'  | 'target_id' | Accept a friend request

#   DELETE    | /api/user/relationship/ | 'cancel'  | 'target_id' | Cancel a friend request
#   DELETE    | /api/user/relationship/ | 'reject'  | 'target_id' | Reject a friend request
#   DELETE    | /api/user/relationship/ | 'remove'  | 'target_id' | Remove a friend
#   DELETE    | /api/user/relationship/ | 'unblock' | 'target_id' | Unblock a user

urlpatterns = [
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),

    # Cange relationship status
    path('relationship/', RelationshipView.as_view(), name='relationship'),
	
    # Friend requesting
    path('friend-request/', FriendRequestView.as_view(), name='friend_request'),
    path('friend/list/<int:id>/', ListFriendsView.as_view(), name='list_friends'),

    # Blocking/unblocking users / removing friends
    path('modify-friendship/', ModifyFriendshipView.as_view(), name='modify_friendship'),

    path('update-avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('update-user-info/', UpdateUserInfoView.as_view(), name='update_user_info'),
]