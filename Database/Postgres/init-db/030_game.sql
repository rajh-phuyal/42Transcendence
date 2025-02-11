-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 030_game.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the enum type: 'barelyaschema.game_state'..."
CREATE TYPE barelyaschema.game_state AS ENUM ('pending', 'countdown', 'ongoing', 'paused', 'finished', 'quited');

\! echo -e "creating the table: 'barelyaschema.game'..."
CREATE TABLE IF NOT EXISTS barelyaschema.game
(
	id SERIAL PRIMARY KEY,
	state barelyaschema.game_state NOT NULL DEFAULT 'pending',
	map_number INT NOT NULL,
	powerups BOOLEAN NOT NULL,
	tournament_id INT,
	deadline TIMESTAMP,
	finish_time TIMESTAMP
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.game OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 030_game.sql \e[0m"
