from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('api/', include('rest_framework.urls')),
	path('user/', include('user.urls')),
	path('chat/', include('chat.urls')),
    path('game/', include('game.urls')),
    path('tournament/', include('tournament.urls')),
]
