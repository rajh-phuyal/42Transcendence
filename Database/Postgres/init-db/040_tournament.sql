-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 040_tournament.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the enum type: 'barelyaschema.game_state'..."
CREATE TYPE barelyaschema.tournament_state AS ENUM ('setup', 'ongoing', 'finished');

\! echo -e "creating the table: 'barelyaschema.tournament'..."
CREATE TABLE IF NOT EXISTS barelyaschema.tournament
(
	id SERIAL PRIMARY KEY,
	state barelyaschema.tournament_state NOT NULL DEFAULT 'setup',
	name VARCHAR(23) NOT NULL,
	local_tournament BOOLEAN NOT NULL,
	public_tournament BOOLEAN NOT NULL,
	map_number INT NOT NULL,
	powerups BOOLEAN NOT NULL,
	finish_time TIMESTAMP
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.tournament OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 040_tournament.sql \e[0m"
