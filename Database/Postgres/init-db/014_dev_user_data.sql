\! echo -e "\e[1m START of 014_dev_user_data.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "Creating the table: 'barelyaschema.dev_user_data' with all necessary fields..."

CREATE TABLE IF NOT EXISTS barelyaschema."dev_user_data" (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(150) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES barelyaschema."user"(id)
);

\! echo -e "Changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema."dev_user_data" OWNER TO "${POSTGRES_USER}";

\! echo -e "\e[1m END of 014_dev_user_data.sql \e[0m"
