-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 041_tournament_match.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.tournament_match'..."
CREATE TABLE IF NOT EXISTS barelyaschema.tournament_match
(
	id SERIAL PRIMARY KEY,
	tournament_id INT NOT NULL,
	match_id INT NOT NULL,
	round INT NOT NULL,
	FOREIGN KEY (tournament_id) REFERENCES barelyaschema.tournament(id),
	FOREIGN KEY (match_id) REFERENCES barelyaschema.match(id),
	CONSTRAINT unique_tournament_match UNIQUE (tournament_id, match_id, round)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.tournament_match OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_tournament_match;
-- DROP INDEX IF EXISTS idx_tournament_match;
-- CREATE INDEX IF NOT EXISTS idx_tournament_match ON barelyaschema.tournament_match USING btree(tournament_id, match_id);

\! echo -e "\e[1m END of 041_tournament_match.sql \e[0m"
