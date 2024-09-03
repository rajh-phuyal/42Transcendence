import psycopg2

# Database connection details
conn = psycopg2.connect(
    dbname='postgres',
    user='admin',
    password='admin',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

########### Insert user data ###########
insert_user_query = """
INSERT INTO transcendence.user 
	(username)
VALUES
	('anatolii'), ('alex'), ('francisco'), ('rajh'), ('joao')
"""
cur.execute(insert_user_query)
conn.commit()

########### Insert user relationship data ###########
insert_user_relationships_query = """
INSERT INTO transcendence.is_cool_with 
	(first_user_id, second_user_id, blocked_by_first, blocked_by_second, status)
VALUES 
	(1, 2, false, false, 'pending')
	, (1, 3, false, false, 'accepted')
	, (1, 4, false, false, 'rejected')
	, (1, 5, false, false, 'pending')
	, (2, 3, false, false, 'pending')
	, (2, 4, false, false, 'accepted')
	, (2, 5, false, false, 'rejected')
	, (3, 4, false, false, 'pending')
	, (3, 5, false, false, 'accepted')
	, (4, 5, false, false, 'rejected');
"""
cur.execute(insert_user_relationships_query)
conn.commit()

########### Insert map data ###########
with open('blob.jpg', 'rb') as file:
    binary_data = file.read()

insert_map_query = """
INSERT INTO transcendence.map 
	(map_name, map_image)
VALUES
	(%s, %s)
"""
cur.execute(insert_map_query, ('map1', binary_data))
cur.execute(insert_map_query, ('map2', binary_data))
cur.execute(insert_map_query, ('map3', binary_data))
conn.commit()

########### Insert match data ###########
insert_match_query = """
INSERT INTO transcendence.match
	(map_id, end_time, first_player_id, second_player_id, winner_id, status)
VALUES
	(1, '2020-01-01 00:00:00', 1, 2, 1, 'finished') -- anatolii vs alex : winner anatolii
	, (2, '2020-01-01 00:00:00', 1, 3, 1, 'finished') -- anatolii vs francisco : winner anatolii
	, (3, '2020-01-01 00:00:00', 1, 4, 1, 'finished') -- anatolii vs rajh : winner anatolii
	, (3, '2020-01-01 00:00:00', 1, 5, 1, 'finished') -- anatolii vs joao : winner anatolii
	, (2, '2020-01-01 00:00:00', 2, 3, 2, 'finished') -- alex vs francisco : winner alex
	, (2, '2020-01-01 00:00:00', 2, 4, 2, 'finished') -- alex vs rajh : winner alex
	, (3, '2020-01-01 00:00:00', 2, 5, 2, 'finished') -- alex vs joao : winner alex
	, (2, '2020-01-01 00:00:00', 3, 4, 3, 'finished') -- francisco vs rajh : winner francisco
	, (1, '2020-01-01 00:00:00', 3, 5, 3, 'finished') -- francisco vs joao : winner francisco
	, (3, '2020-01-01 00:00:00', 4, 5, 4, 'finished'); -- rajh vs joao : winner rajh
"""
cur.execute(insert_match_query)
conn.commit()

########### Insert match score data ###########
insert_match_score_query = """
INSERT INTO transcendence.match_score
	(match_id, sets_played, first_player_points, second_player_points)
VALUES
	(1, 15, 10, 5) -- anatolii vs alex : 10-5
	, (2, 10, 7, 3) -- anatolii vs francisco : 7-3
	, (3, 9, 5, 4) -- anatolii vs rajh : 5-4
	, (4, 6, 4, 2) -- anatolii vs joao : 4-2
	, (5, 8, 5, 3) -- alex vs francisco : 5-3
	, (6, 9, 7, 2) -- alex vs rajh : 7-2
	, (7, 3, 2, 1) -- alex vs joao : 2-1
	, (8, 6, 5, 1) -- francisco vs rajh : 5-1
	, (9, 4, 3, 1) -- francisco vs joao : 3-1 
	, (10, 12, 7, 5); -- rajh vs joao : 7-5
"""
cur.execute(insert_match_score_query)
conn.commit()

########### Insert tournament data ###########
insert_tournament_query = """
INSERT INTO transcendence.tournament
	(tournament_name, tournament_map_id, min_level, max_level, end_time, number_of_rounds, status)
VALUES
	('tournament1', 1, 0, 9999, '2222-01-01 00:00:00', 1, 'finished')
	, ('tournament2', 2, 0, 9999, NULL, 1, 'not_started')
	, ('tournament3', 3, 0, 9999, NULL, 1, 'not_started');
"""
cur.execute(insert_tournament_query)
conn.commit()

########### Insert tournament match data ###########
insert_tournament_match_query = """
INSERT INTO transcendence.tournament_match
	(tournament_id, match_id, round)
VALUES
	(1, 1, 1) -- tournament1 : anatolii vs alex
	, (1, 2, 1) -- tournament1 : anatolii vs francisco
	, (1, 3, 1) -- tournament1 : anatolii vs rajh
	, (1, 4, 1) -- tournament1 : anatolii vs joao
	, (1, 5, 1) -- tournament1 : alex vs francisco
	, (1, 6, 1) -- tournament1 : alex vs rajh
	, (1, 7, 1) -- tournament1 : alex vs joao
	, (1, 8, 1) -- tournament1 : francisco vs rajh
	, (1, 9, 1) -- tournament1 : francisco vs joao
	, (1, 10, 1); -- tournament1 : rajh vs joao
"""
cur.execute(insert_tournament_match_query)
conn.commit()

########### Insert tournament registration data ###########

insert_tournament_registration_query = """
INSERT INTO transcendence.tournament_register
	(tournament_id, player_id)
VALUES
	(1, 1) -- tournament1 : anatolii
	, (1, 2) -- tournament1 : alex
	, (1, 3) -- tournament1 : francisco
	, (1, 4) -- tournament1 : rajh
	, (1, 5); -- tournament1 : joao
"""
cur.execute(insert_tournament_registration_query)
conn.commit()

########### Insert tournament standings data ###########
insert_tournament_standings_query = """
INSERT INTO transcendence.tournament_standings
	(tournament_id, player_id, matches_played, matches_won, matches_lost, total_points, current_score)
VALUES
	(1, 1, 4, 4, 0, 26, 4) -- anatolii : 4 matches, 4 wins, 0 losses, 12 points, 1 score
	, (1, 2, 4, 3, 1, 24, 3) -- alex : 4 matches, 3 wins, 1 loss, 9 points, 2 score
	, (1, 3, 4, 2, 2, 18, 2) -- francisco : 4 matches, 2 wins, 2 losses, 6 points, 3 score
	, (1, 4, 4, 1, 3, 14, 1) -- rajh : 4 matches, 1 win, 3 losses, 3 points, 4 score
	, (1, 5, 4, 0, 4, 10, 0); -- joao : 4 matches, 0 wins, 4 losses, 0 points, 5 score
"""
cur.execute(insert_tournament_standings_query)
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()