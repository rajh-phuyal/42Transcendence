-- [astein]:
-- This is the third file of the configuration of the postgres db

\! echo -e "\e[1m START of 011_is_cool_with.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.is_cool_with'..."
CREATE TABLE IF NOT EXISTS barelyaschema.is_cool_with
(
	id SERIAL PRIMARY KEY,
	first_user_id INT NOT NULL,
	second_user_id INT NOT NULL,
	blocked_by_first BOOLEAN NOT NULL DEFAULT FALSE,
	blocked_by_second BOOLEAN NOT NULL DEFAULT FALSE,
	status barelyaschema.relationship_status_enum NOT NULL DEFAULT 'pending',
	FOREIGN KEY (first_user_id) REFERENCES barelyaschema.users(id),
	FOREIGN KEY (second_user_id) REFERENCES barelyaschema.users(id),
	CONSTRAINT unique_relationship UNIQUE (first_user_id, second_user_id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.is_cool_with OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_is_cool_with
-- DROP INDEX IF EXISTS idx_is_cool_with;
-- CREATE INDEX IF NOT EXISTS idx_is_cool_with ON transcendence.is_cool_with USING btree(first_user_id, second_user_id);

\! echo -e "\e[1m END of 011_is_cool_with.sql \e[0m"