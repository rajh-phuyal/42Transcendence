
-- Table: transcendence.is_cool_with

-- DROP TABLE IF EXISTS transcendence.is_cool_with;

CREATE TABLE IF NOT EXISTS transcendence.is_cool_with
(
	id SERIAL PRIMARY KEY
	, first_user_id INT NOT NULL
	, second_user_id INT NOT NULL
	, blocked_by_first BOOLEAN NOT NULL DEFAULT FALSE
	, blocked_by_second BOOLEAN NOT NULL DEFAULT FALSE
	, status transcendence.relationship_status_enum NOT NULL DEFAULT 'pending'
	, FOREIGN KEY (first_user_id) REFERENCES transcendence.user(id)
	, FOREIGN KEY (second_user_id) REFERENCES transcendence.user(id)
);

ALTER TABLE IF EXISTS transcendence.is_cool_with OWNER to "admin";

-- Index: idx_is_cool_with

-- DROP INDEX IF EXISTS idx_is_cool_with;

CREATE INDEX IF NOT EXISTS idx_is_cool_with ON transcendence.is_cool_with USING btree(first_user_id, second_user_id);