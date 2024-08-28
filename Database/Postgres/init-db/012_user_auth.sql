-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 012_user_auth.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.user_auth'..."
CREATE TABLE IF NOT EXISTS barelyaschema.user_auth
(
	id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	passwordHash VARCHAR(255) NOT NULL,
	passwordSalt VARCHAR(255) NOT NULL,
	FOREIGN KEY (user_id) REFERENCES barelyaschema.users(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.user_auth OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_user_auth
-- DROP INDEX IF EXISTS idx_user_auth;
-- CREATE INDEX IF NOT EXISTS idx_user_auth ON barelyaschema.user_auth USING btree(user_id);

\! echo -e "\e[1m END of 012_user_auth.sql \e[0m"
