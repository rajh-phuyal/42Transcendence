-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 041_tournament_member.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.tournament_member'..."
CREATE TABLE IF NOT EXISTS barelyaschema.tournament_member
(
	id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	tournament_id INT NOT NULL,
	tournament_alias VARCHAR(150),
	accepted BOOLEAN NOT NULL DEFAULT FALSE,
	finish_place INT,
	FOREIGN KEY (user_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (tournament_id) REFERENCES barelyaschema.tournament(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.tournament_member OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 041_tournament_member.sql \e[0m"
