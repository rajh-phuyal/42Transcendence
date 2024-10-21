-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 050_conversation.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.conversation'..."
CREATE TABLE IF NOT EXISTS barelyaschema.conversation
(
	id SERIAL PRIMARY KEY,
	name VARCHAR(255),
	is_group_conversation BOOLEAN NOT NULL DEFAULT FALSE,
	is_editable BOOLEAN NOT NULL DEFAULT FALSE
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.conversation OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 050_conversation.sql \e[0m"
