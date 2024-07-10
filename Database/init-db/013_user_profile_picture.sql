\c postgres

-- Table: transcendence.user_profile_picture

-- DROP TABLE IF EXISTS transcendence.user_profile_picture;

CREATE TABLE IF NOT EXISTS transcendence.user_profile_picture
(
	id SERIAL PRIMARY KEY
	, user_id INT NOT NULL
	, profile_picture BYTEA NOT NULL
	, FOREIGN KEY (user_id) REFERENCES transcendence.user(id)
);

ALTER TABLE IF EXISTS transcendence.user_profile_picture OWNER to "admin";

-- Index: idx_user_profile_picture

-- DROP INDEX IF EXISTS idx_user_profile_picture;

CREATE INDEX IF NOT EXISTS idx_user_profile_picture ON transcendence.user_profile_picture USING btree(user_id);