-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 030_match.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.match'..."
CREATE TABLE IF NOT EXISTS barelyaschema.match
(
	id SERIAL PRIMARY KEY,
	map_id INT NOT NULL,
	end_time TIMESTAMP,
	first_player_id INT NOT NULL,
	second_player_id INT NOT NULL,
	winner_id INT,
	status barelyaschema.progress_status_enum NOT NULL DEFAULT 'not_started',
	FOREIGN KEY (map_id) REFERENCES barelyaschema.map(id),
	FOREIGN KEY (first_player_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (second_player_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (winner_id) REFERENCES barelyaschema.user(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.match OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_match
-- DROP INDEX IF EXISTS idx_match;
-- CREATE INDEX IF NOT EXISTS idx_match ON barelyaschema.match USING btree(first_player_id, second_player_id, winner_id);

\! echo -e "\e[1m END of 030_match.sql \e[0m"
