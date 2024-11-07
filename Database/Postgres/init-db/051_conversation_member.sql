-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 051_conversation_member.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.conversation_member'..."
CREATE TABLE IF NOT EXISTS barelyaschema.conversation_member
(
	id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	conversation_id INT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (conversation_id) REFERENCES barelyaschema.conversation(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.conversation_member OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 051_conversation_member.sql \e[0m"
