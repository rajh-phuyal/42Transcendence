-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 050_chat.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.chat'..."
CREATE TABLE IF NOT EXISTS barelyaschema.chat
(
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.chat OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 050_chat.sql \e[0m"
