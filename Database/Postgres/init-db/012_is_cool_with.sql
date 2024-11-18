-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 012_is_cool_with.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the enum type: 'barelyaschema.cool_status'..."
CREATE TYPE barelyaschema.cool_status AS ENUM ('pending', 'accepted');

\! echo -e "creating the table: 'barelyaschema.is_cool_with'..."
CREATE TABLE IF NOT EXISTS barelyaschema.is_cool_with
(
	id SERIAL PRIMARY KEY,
	requester_id INT NOT NULL,
	requestee_id INT NOT NULL,
	status barelyaschema.cool_status NOT NULL DEFAULT 'pending',
    notification_id INT,
	FOREIGN KEY (requester_id) REFERENCES barelyaschema.user(id),
	FOREIGN KEY (requestee_id) REFERENCES barelyaschema.user(id),
    FOREIGN KEY (notification_id) REFERENCES barelyaschema.notification(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.is_cool_with OWNER to "${POSTGRES_USER}";

-- Index: idx_is_cool_with
DROP INDEX IF EXISTS idx_is_cool_with;
CREATE UNIQUE INDEX IF NOT EXISTS idx_is_cool_with 
ON barelyaschema.is_cool_with (
    LEAST(requester_id, requestee_id),
    GREATEST(requester_id, requestee_id)
);

\! echo -e "\e[1m END of 012_is_cool_with.sql \e[0m"