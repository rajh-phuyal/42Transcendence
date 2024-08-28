-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 043_tournament_standings.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.tournament_standings'..."
CREATE TABLE IF NOT EXISTS barelyaschema.tournament_standings
(
	id SERIAL PRIMARY KEY,
	tournament_id INT NOT NULL,
	player_id INT NOT NULL,
	matches_played INT NOT NULL,
	matches_won INT NOT NULL,
	matches_lost INT NOT NULL,
	total_points INT NOT NULL,
	current_score INT NOT NULL,
	FOREIGN KEY (tournament_id) REFERENCES barelyaschema.tournament(id),
	FOREIGN KEY (player_id) REFERENCES barelyaschema.users(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.tournament_standings OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_tournament_standings
-- DROP INDEX IF EXISTS idx_tournament_standings;
-- CREATE INDEX IF NOT EXISTS idx_tournament_standings ON barelyaschema.tournament_standings USING btree(tournament_id, player_id);

\! echo -e "\e[1m END of 043_tournament_standings.sql \e[0m"
