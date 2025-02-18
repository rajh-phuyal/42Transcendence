from django.urls import path

from user.views import (
    SearchView,
    ProfileView,
	RelationshipView,
    ListFriendsView,
    UpdateAvatarView,
    UpdateUserInfoView
)

urlpatterns = [
    path('search/<str:search>/', SearchView.as_view(), name='search'),
    path('profile/<int:targetUserId>/', ProfileView.as_view(), name='profile'),
    path('relationship/<str:action>/<int:targetUserId>/', RelationshipView.as_view(), name='relationship'),
    path('friend/list/<int:targetUserId>/', ListFriendsView.as_view(), name='list_friends'),
    path('update-avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('update-user-info/', UpdateUserInfoView.as_view(), name='update_user_info'),
]