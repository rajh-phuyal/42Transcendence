\c postgres

-- Table: transcendence.user

-- DROP TABLE IF EXISTS transcendence.user;

CREATE TABLE IF NOT EXISTS transcendence.user
(
	id SERIAL PRIMARY KEY
	, username VARCHAR(255) NOT NULL
);

ALTER TABLE IF EXISTS transcendence.user OWNER to "admin";

-- Index: idx_user

-- DROP INDEX IF EXISTS idx_user;

CREATE INDEX IF NOT EXISTS idx_user ON transcendence.user USING btree(username);