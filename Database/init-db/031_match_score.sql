
-- Table: transcendence.match_score

-- DROP TABLE IF EXISTS transcendence.match_score;

CREATE TABLE IF NOT EXISTS transcendence.match_score
(
	id SERIAL PRIMARY KEY
	, match_id INT NOT NULL
	, sets_played INT NOT NULL
	, first_player_points INT NOT NULL
	, second_player_points INT NOT NULL
);

ALTER TABLE IF EXISTS transcendence.match_score OWNER to "admin";

-- Index: idx_match_score

-- DROP INDEX IF EXISTS idx_match_score;

CREATE INDEX IF NOT EXISTS idx_match_score ON transcendence.match_score USING btree(match_id);