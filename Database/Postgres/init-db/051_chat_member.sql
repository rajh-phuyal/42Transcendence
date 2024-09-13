-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 051_chat_member.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.chat_member'..."
CREATE TABLE IF NOT EXISTS barelyaschema.chat_member
(
	id SERIAL PRIMARY KEY,
	chat_id INT NOT NULL,
	user_id INT NOT NULL,
	FOREIGN KEY (chat_id) REFERENCES barelyaschema.chat(id),
	FOREIGN KEY (user_id) REFERENCES barelyaschema.user(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.chat_member OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 051_chat_member.sql \e[0m"
