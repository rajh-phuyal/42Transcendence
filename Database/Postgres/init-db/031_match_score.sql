-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 031_match_score.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.match_score'..."
CREATE TABLE IF NOT EXISTS barelyaschema.match_score
(
	id SERIAL PRIMARY KEY,
	match_id INT NOT NULL UNIQUE,
	sets_played INT NOT NULL,
	first_player_points INT NOT NULL,
	second_player_points INT NOT NULL
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.match_score OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_match_score
-- DROP INDEX IF EXISTS idx_match_score;
-- CREATE INDEX IF NOT EXISTS idx_match_score ON barelyaschema.match_score USING btree(match_id);

\! echo -e "\e[1m END of 031_match_score.sql \e[0m"
