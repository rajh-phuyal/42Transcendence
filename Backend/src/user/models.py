from django.db import models

# Table: barelyaschema.user
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=False)
    pswd = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = '"barelyaschema"."user"'
