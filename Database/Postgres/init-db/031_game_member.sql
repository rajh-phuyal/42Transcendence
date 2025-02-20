-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 031_game_member.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the enum type: 'barelyaschema.game_result'..."
CREATE TYPE barelyaschema.game_result AS ENUM ('pending', 'won', 'lost');

\! echo -e "creating the table: 'barelyaschema.game_member'..."
CREATE TABLE IF NOT EXISTS barelyaschema.game_member
(
	id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	game_id INT NOT NULL,
	points INT NOT NULL DEFAULT 0,
	result barelyaschema.game_result NOT NULL DEFAULT 'pending',
	powerup_big BOOLEAN NOT NULL DEFAULT FALSE,
	powerup_fast BOOLEAN NOT NULL DEFAULT FALSE,
	powerup_slow BOOLEAN NOT NULL DEFAULT FALSE,
    admin BOOLEAN NOT NULL DEFAULT FALSE,
	FOREIGN KEY (user_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (game_id) REFERENCES barelyaschema.game(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.game_member OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 031_game_member.sql \e[0m"
