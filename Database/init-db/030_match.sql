
-- Table: transcendence.match

-- DROP TABLE IF EXISTS transcendence.match;

CREATE TABLE IF NOT EXISTS transcendence.match
(
	id SERIAL PRIMARY KEY
	, map_id INT NOT NULL
	, end_time TIMESTAMP
	, first_player_id INT NOT NULL
	, second_player_id INT NOT NULL
	, winner_id INT
	, status transcendence.progress_status_enum NOT NULL DEFAULT 'not_started'
	, FOREIGN KEY (map_id) REFERENCES transcendence.map(id)
	, FOREIGN KEY (first_player_id) REFERENCES transcendence.user(id)
	, FOREIGN KEY (second_player_id) REFERENCES transcendence.user(id)
	, FOREIGN KEY (winner_id) REFERENCES transcendence.user(id)
);

ALTER TABLE IF EXISTS transcendence.match OWNER to "admin";

-- Index: idx_match

-- DROP INDEX IF EXISTS idx_match;

CREATE INDEX IF NOT EXISTS idx_match ON transcendence.match USING btree(first_player_id, second_player_id, winner_id);