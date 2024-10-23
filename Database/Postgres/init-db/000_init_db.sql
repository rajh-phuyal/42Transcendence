-- [astein]:
-- This is the first file of the configuration of the postgres db
-- Steps:
--   - creating database
--   - creating custom schema
--   - granting privileges for the db user

\! echo -e "\e[1m START of 000_init_db.sql \e[0m"


\! echo -e "\e[1m Creating Database: ${DB_NAME} \e[0m"
CREATE DATABASE ${DB_NAME};

-- Introduce a short delay to allow PostgreSQL to register the new database
DO $$ 
BEGIN
   PERFORM pg_sleep(1);
END $$;

\! echo -e "\e[1m Connect to the newly created database \e[0m"
\c ${DB_NAME}

-- Comment: somehow this database is needed. If drop it I get this msg:
-- "psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  database "admin" does not exist"
-- \! echo -e "\e[1m Deleting template db admin \e[0m"
-- DROP DATABASE IF EXISTS admin;

\! echo -e "\e[1m Creating Schema: barelyaschema \e[0m"
CREATE SCHEMA IF NOT EXISTS barelyaschema AUTHORIZATION "${POSTGRES_USER}";

\! echo -e "\e[1m Grant privileges on the public schema to the specified user: ${POSTGRES_USER} \e[0m"
GRANT USAGE, CREATE ON SCHEMA barelyaschema TO "${POSTGRES_USER}";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA barelyaschema TO "${POSTGRES_USER}";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA barelyaschema TO "${POSTGRES_USER}";

 \! echo -e "\e[1m END of 000_init_db.sql \e[0m"