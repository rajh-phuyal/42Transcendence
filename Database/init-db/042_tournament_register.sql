
-- Table: transcendence.tournament_register

-- DROP TABLE IF EXISTS transcendence.tournament_register;

CREATE TABLE IF NOT EXISTS transcendence.tournament_register
(
	id SERIAL PRIMARY KEY
	, player_id INT NOT NULL
	, tournament_id INT
	, FOREIGN KEY (player_id) REFERENCES transcendence.user(id)
	, FOREIGN KEY (tournament_id) REFERENCES transcendence.tournament(id)
);

ALTER TABLE IF EXISTS transcendence.tournament_register OWNER to "admin";

-- Index: idx_tournament_register

-- DROP INDEX IF EXISTS idx_tournament_register;

CREATE INDEX IF NOT EXISTS idx_tournament_register ON transcendence.tournament_register USING btree(player_id, tournament_id);