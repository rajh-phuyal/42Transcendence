
-- Table: transcendence.tournament

-- DROP TABLE IF EXISTS transcendence.tournament;

CREATE TABLE IF NOT EXISTS transcendence.tournament
(
	id SERIAL PRIMARY KEY
	, tournament_name VARCHAR(255) NOT NULL
	, tournament_map_id INT NOT NULL
	, min_level INT NOT NULL
	, max_level INT NOT NULL
	, end_time TIMESTAMP
	, number_of_rounds INT NOT NULL
	, status transcendence.progress_status_enum NOT NULL DEFAULT 'not_started'
	, FOREIGN KEY (tournament_map_id) REFERENCES transcendence.map(id)
);

ALTER TABLE IF EXISTS transcendence.tournament OWNER to "admin";

-- Index: idx_tournament

-- DROP INDEX IF EXISTS idx_tournament;

CREATE INDEX IF NOT EXISTS idx_tournament ON transcendence.tournament USING btree(tournament_name, tournament_map_id, min_level, max_level, end_time, number_of_rounds, status);