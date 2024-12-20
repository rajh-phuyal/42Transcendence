from django.db import models

# TODO:
# Since all of this is old we should delete the code below after checking it...

# # NOTE:
# # If table column changes, db_column='tournament_id' 
# # could be used to map to the correct column in the database 
# # without changing the column name in the model

# # Table: transcendence.user_profile_picture
# class UserProfilePicture(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	user_id = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
# 	profile_picture = models.BinaryField(null=False)

# 	class Meta:
# 		db_table = 'transcendence.user_profile_picture'
