-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 042_tournament_register.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.tournament_register'..."
CREATE TABLE IF NOT EXISTS barelyaschema.tournament_register
(
	id SERIAL PRIMARY KEY,
	player_id INT NOT NULL,
	tournament_id INT NOT NULL,
	FOREIGN KEY (player_id) REFERENCES barelyaschema.users(id),
	FOREIGN KEY (tournament_id) REFERENCES barelyaschema.tournament(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.tournament_register OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_tournament_register
-- DROP INDEX IF EXISTS idx_tournament_register;
-- CREATE INDEX IF NOT EXISTS idx_tournament_register ON barelyaschema.tournament_register USING btree(player_id, tournament_id);

\! echo -e "\e[1m END of 042_tournament_register.sql \e[0m"
