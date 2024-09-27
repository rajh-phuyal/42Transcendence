\! echo -e "\e[1m START of 010_user.sql \e[0m"

-- Switching to our DB
\c ${DB_NAME}

\! echo -e "Creating the table: 'barelyaschema.user' with all necessary fields..."

CREATE TABLE IF NOT EXISTS barelyaschema."user" (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
);

\! echo -e "Changing the ownership of the table to user '${POSTGRES_USER}'"
ALTER TABLE IF EXISTS barelyaschema."user" OWNER TO "${POSTGRES_USER}";

\! echo -e "\e[1m END of 010_user.sql \e[0m"
