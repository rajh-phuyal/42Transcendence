-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 013_user_profile_picture.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.user_profile_picture'..."
CREATE TABLE IF NOT EXISTS barelyaschema.user_profile_picture
(
	id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	profile_picture BYTEA NOT NULL,
	FOREIGN KEY (user_id) REFERENCES barelyaschema.users(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.user_profile_picture OWNER to "${POSTGRES_USER}";

-- [astein] this was done by joao. seems smart but i don't fully get it yet.
-- Index: idx_user_profile_picture
-- DROP INDEX IF EXISTS idx_user_profile_picture;
-- CREATE INDEX IF NOT EXISTS idx_user_profile_picture ON barelyaschema.user_profile_picture USING btree(user_id);

\! echo -e "\e[1m END of 013_user_profile_picture.sql \e[0m"
