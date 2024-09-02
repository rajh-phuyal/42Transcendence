-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 020_map.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.map'..."
CREATE TABLE IF NOT EXISTS barelyaschema.map
(
	id SERIAL PRIMARY KEY,
	map_name VARCHAR(255) NOT NULL,
	map_image BYTEA NOT NULL
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.map OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_map
-- DROP INDEX IF EXISTS idx_map;
-- CREATE INDEX IF NOT EXISTS idx_map ON barelyaschema.map USING btree(map_name);

\! echo -e "\e[1m END of 020_map.sql \e[0m"
