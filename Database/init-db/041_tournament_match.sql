\c postgres

-- Table: transcendence.tournament_match

-- DROP TABLE IF EXISTS transcendence.tournament_match;

CREATE TABLE IF NOT EXISTS transcendence.tournament_match
(
	id SERIAL PRIMARY KEY
	, tournament_id INT NOT NULL
	, match_id INT NOT NULL
	, round INT NOT NULL
	, FOREIGN KEY (tournament_id) REFERENCES transcendence.tournament(id)
	, FOREIGN KEY (match_id) REFERENCES transcendence.match(id)
	, CONSTRAINT unique_tournament_match UNIQUE (tournament_id, match_id, round)
);

ALTER TABLE IF EXISTS transcendence.tournament_match OWNER to "admin";

-- Index: idx_tournament_match;

-- DROP INDEX IF EXISTS idx_tournament_match;

CREATE INDEX IF NOT EXISTS idx_tournament_match ON transcendence.tournament_match USING btree(tournament_id, match_id);