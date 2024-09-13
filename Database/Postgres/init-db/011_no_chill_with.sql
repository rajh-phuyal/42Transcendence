-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 011_no_chill_with.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the table: 'barelyaschema.no_chill_with'..."
CREATE TABLE IF NOT EXISTS barelyaschema.no_chill_with
(
	id SERIAL PRIMARY KEY,
	blocker_id INT NOT NULL,
	blocked_id INT NOT NULL,
	FOREIGN KEY (blocker_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (blocked_id) REFERENCES barelyaschema.user(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.no_chill_with OWNER to "${POSTGRES_USER}";

-- Index: idx_no_chill_with
DROP INDEX IF EXISTS idx_no_chill_with;
CREATE INDEX IF NOT EXISTS idx_no_chill_with 
ON barelyaschema.no_chill_with (blocker_id, blocked_id);

\! echo -e "\e[1m END of 011_no_chill_with.sql \e[0m"