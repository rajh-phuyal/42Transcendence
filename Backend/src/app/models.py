from django.db import models

# # NOTE:
# # If table column changes, db_column='tournament_id' 
# # could be used to map to the correct column in the database 
# # without changing the column name in the model

# # Enum for relationship status
# relationship_status_enum = [
#     ('pending', 'Pending'),
#     ('accepted', 'Accepted'),
#     ('rejected', 'Rejected'),
#     ('blocked', 'Blocked')
# ]

# # Enum for progress status
# progress_status_enum = [
#     ('not_started', 'Not Started'),
#     ('in_progress', 'In Progress'),
#     ('finished', 'Finished')
# ]

# # Table: transcendence.user
# class User(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	username = models.CharField(max_length=255, null=False)

# 	class Meta:
# 		db_table = 'transcendence.user'

# # Table: transcendence.is_cool_with
# class IsCoolWith(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	first_user_id = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
# 	second_user_id = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
# 	blocked_by_first = models.BooleanField(null=False, default=False)
# 	blocked_by_second = models.BooleanField(null=False, default=False)
# 	status = models.CharField(max_length=50, choices=relationship_status_enum, default='pending')

# 	class Meta:
# 		db_table = 'transcendence.is_cool_with'
# 		unique_together = ('first_user_id', 'second_user_id') # This is to ensure that there is only one entry for a pair of users

# # Table: transcendence.user_auth
# class UserAuth(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	user_id = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
# 	passwordHash = models.CharField(max_length=255, null=False)
# 	passwordSalt = models.CharField(max_length=255, null=False)

# 	class Meta:
# 		db_table = 'transcendence.user_auth'

# # Table: transcendence.user_profile_picture
# class UserProfilePicture(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	user_id = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
# 	profile_picture = models.BinaryField(null=False)

# 	class Meta:
# 		db_table = 'transcendence.user_profile_picture'

# # Table: transcendence.map
# class Map(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	map_name = models.CharField(max_length=255, null=False)
# 	map_image = models.BinaryField(null=False)

# 	class Meta:
# 		db_table = 'transcendence.map'

# # Table: transcendence.match
# class Match(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	map_id = models.ForeignKey(Map, null=False)
# 	first_player_id = models.ForeignKey(User, null=False)
# 	second_player_id = models.ForeignKey(User, null=False) #maybe should not be cascade because if user is deleted, match should still exist
# 	winner_id = models.ForeignKey(User, null=False)
# 	status = models.CharField(max_length=50 , choices=progress_status_enum, default='not_started')

# 	class Meta:
# 		db_table = 'transcendence.match'

# # Table: transcendence.match_score
# class MatchScore(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	match_id = models.ForeignKey(Match, unique=True, on_delete=models.CASCADE)
# 	sets_played = models.IntegerField(null=False)
# 	first_player_points = models.IntegerField(null=False)
# 	second_player_points = models.IntegerField(null=False)

# 	class Meta:
# 		db_table = 'transcendence.match_score'

# #Table: transcendence.tournament
# class Tournament(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	tournament_name = models.CharField(max_length=255, null=False)
# 	tournament_map_id = models.ForeignKey(Map, null=False)
# 	min_level = models.IntegerField(null=False)
# 	max_level = models.IntegerField(null=False)
# 	end_time = models.DateTimeField(null=False)
# 	number_of_rounds = models.IntegerField(null=False)
# 	status = models.CharField(max_length=50, choices=progress_status_enum, default='not_started')

# 	class Meta:
# 		db_table = 'transcendence.tournament'

# #Table: transcendence.tournament_match
# class TournamentMatch(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	tournament_id = models.ForeignKey(Tournament, null=False, on_delete=models.CASCADE)
# 	match_id = models.ForeignKey(Match, null=False, on_delete=models.CASCADE)
# 	round = models.IntegerField(null=False)

# 	class Meta:
# 		db_table = 'transcendence.tournament_match'
# 		unique_together = ('tournament_id', 'match_id', 'round')


# #Table: transcendence.tournament_register
# class TournamentRegister(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	player_id = models.ForeignKey(User, null=False)
# 	tournament_id = models.ForeignKey(Tournament, null=False, on_delete=models.CASCADE)

# 	class Meta:
# 		db_table = 'transcendence.tournament_register'
# 		unique_together = ('tournament_id', 'player_id')

# #Table: transcendence.tournament_standings
# class TournamentStandings(models.Model):

# 	id = models.AutoField(primary_key=True)
# 	tournament_id = models.ForeignKey(Tournament, null=False, on_delete=models.CASCADE)
# 	player_id = models.ForeignKey(User, null=False)
# 	matches_played = models.IntegerField(null=False)
# 	matches_won = models.IntegerField(null=False)
# 	matches_lost = models.IntegerField(null=False)
# 	total_points = models.IntegerField(null=False)
# 	current_score = models.IntegerField

# 	class Meta:
# 		db_table = 'transcendence.tournament_standings'
# 		unique_together = ('tournament_id', 'player_id')
