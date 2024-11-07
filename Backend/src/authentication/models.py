from django.db import models
from django.conf import settings

# Create your models here.
class DevUserData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, null=True)
    access_token = models.TextField()
    refresh_token = models.TextField()

    class Meta:
        db_table = '"barelyaschema"."dev_user_data"'