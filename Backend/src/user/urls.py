from django.urls import path
from .views import (
    ProfileView,
	RelationshipView,
    ListFriendsView,
    UpdateAvatarView,
    UpdateUserInfoView
)

urlpatterns = [
    path('profile/<int:id>/', ProfileView.as_view(), name='profile'),
    path('relationship/', RelationshipView.as_view(), name='relationship'),
    path('friend/list/<int:id>/', ListFriendsView.as_view(), name='list_friends'),
    path('update-avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('update-user-info/', UpdateUserInfoView.as_view(), name='update_user_info'),
]