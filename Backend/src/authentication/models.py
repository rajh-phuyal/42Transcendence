from django.db import models
from django.conf import settings

# Create your models here.
class DevUserData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to your custom User model
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dev_user_data'  # Custom table name for development purposes
