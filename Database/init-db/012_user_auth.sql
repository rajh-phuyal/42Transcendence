
-- Table: transcendence.user_auth

-- DROP TABLE IF EXISTS transcendence.user_auth;

CREATE TABLE IF NOT EXISTS transcendence.user_auth
(
	id SERIAL PRIMARY KEY
	, user_id INT NOT NULL
	, passwordHash VARCHAR(255) NOT NULL
	, passwordSalt VARCHAR(255) NOT NULL
	, FOREIGN KEY (user_id) REFERENCES transcendence.user(id)
);

ALTER TABLE IF EXISTS transcendence.user_auth OWNER to "admin";

-- Index: idx_user_auth

-- DROP INDEX IF EXISTS idx_user_auth;

CREATE INDEX IF NOT EXISTS idx_user_auth ON transcendence.user_auth USING btree(user_id);