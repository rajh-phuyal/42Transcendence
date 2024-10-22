-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 040_tournament.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.tournament'..."
CREATE TABLE IF NOT EXISTS barelyaschema.tournament
(
	id SERIAL PRIMARY KEY,
	tournament_name VARCHAR(255) NOT NULL,
	tournament_map_id INT NOT NULL,
	min_level INT NOT NULL,
	max_level INT NOT NULL,
	end_time TIMESTAMP,
	number_of_rounds INT NOT NULL,
	status barelyaschema.progress_status_enum NOT NULL DEFAULT 'not_started',
	FOREIGN KEY (tournament_map_id) REFERENCES barelyaschema.map(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.tournament OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_tournament
-- DROP INDEX IF EXISTS idx_tournament;
-- CREATE INDEX IF NOT EXISTS idx_tournament ON barelyaschema.tournament USING btree(tournament_name, tournament_map_id, min_level, max_level, end_time, number_of_rounds, status);

\! echo -e "\e[1m END of 040_tournament.sql \e[0m"
