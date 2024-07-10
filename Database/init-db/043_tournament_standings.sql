\c postgres

-- Table: transcendence.tournament_standings

-- DROP TABLE IF EXISTS transcendence.tournament_standings;

CREATE TABLE IF NOT EXISTS transcendence.tournament_standings
(
	id SERIAL PRIMARY KEY
	, tournament_id INT NOT NULL
	, player_id INT NOT NULL
	, matches_played INT NOT NULL
	, matches_won INT NOT NULL
	, matches_lost INT NOT NULL
	, total_points INT NOT NULL
	, current_score INT NOT NULL
	, FOREIGN KEY (tournament_id) REFERENCES transcendence.tournament(id)
	, FOREIGN KEY (player_id) REFERENCES transcendence.user(id)
);

ALTER TABLE IF EXISTS transcendence.tournament_standings OWNER to "admin";

-- Index: idx_tournament_standings

-- DROP INDEX IF EXISTS idx_tournament_standings;

CREATE INDEX IF NOT EXISTS idx_tournament_standings ON transcendence.tournament_standings USING btree(tournament_id, player_id);