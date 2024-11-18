-- [astein]:
-- This is an essential part of the db configuration process!

\! echo -e "\e[1m START of 011_notification.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "creating the enum type: 'barelyaschema.notification_type'..."
CREATE TYPE barelyaschema.notification_type AS ENUM ('friend', 'game', 'tournament');

\! echo -e "creating the table: 'barelyaschema.notification'..."
CREATE TABLE IF NOT EXISTS barelyaschema.notification
(
	id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	seen_at TIMESTAMP,
    img_path VARCHAR(255) NOT NULL,
    redir_path VARCHAR(255) NOT NULL,
    type barelyaschema.notification_type NOT NULL,
    FOREIGN KEY (user_id) REFERENCES barelyaschema.user(id)
);

\! echo -e "changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema.notification OWNER to "${POSTGRES_USER}";

\! echo -e "\e[1m END of 011_notification.sql \e[0m"