-- [astein]:
-- This is the second file of the configuration of the postgres db

\! echo -e "\e[1m START of 010_user.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.users'..."
CREATE TABLE IF NOT EXISTS barelyaschema.users
(
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) NOT NULL
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.users OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- so leave it for later:
-- TODO:
-- CHAT GPT:
-- Index Creation:
-- This part creates an index named idx_user on the username column of the transcendence.user table.
-- An index helps speed up queries that search for or sort data by the username column.
-- The USING btree specifies that the B-tree algorithm is used to create the index, which is the default and most commonly used indexing method in PostgreSQL.
-- OLD CODE:
-- Index: idx_user
-- DROP INDEX IF EXISTS idx_user;
-- CREATE INDEX IF NOT EXISTS idx_user ON transcendence.user USING btree(username);

\! echo -e "\e[1m END of 010_user.sql \e[0m"
