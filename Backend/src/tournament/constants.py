from datetime import timedelta
MAX_PLAYERS_FOR_TOURNAMENT = 6 # Since we only use round robin for now, we limit the number of players to 6 which results in 18 matches
DEADLINE_FOR_TOURNAMENT_GAME_START = timedelta(minutes=1) #TODO: HACKATHON: Change this to not use timedelta here!