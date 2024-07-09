
-- Table: transcendence.map

-- DROP TABLE IF EXISTS transcendence.map;

CREATE TABLE IF NOT EXISTS transcendence.map
(
	id SERIAL PRIMARY KEY
	, map_name VARCHAR(255) NOT NULL
	, map_image BYTEA NOT NULL
);

ALTER TABLE IF EXISTS transcendence.map OWNER to "admin";

-- Index: idx_map

-- DROP INDEX IF EXISTS idx_map;

CREATE INDEX IF NOT EXISTS idx_map ON transcendence.map USING btree(map_name);