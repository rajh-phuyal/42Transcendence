-- Create the database if it doesn't exist
CREATE DATABASE ${DB_NAME};

-- Introduce a short delay to allow PostgreSQL to register the new database
DO $$ 
BEGIN
   PERFORM pg_sleep(1);
END $$;

-- Check if the database is created successfully
\l

-- Connect to the newly created database
\c ${DB_NAME}

-- Grant privileges on the public schema to the specified user
GRANT USAGE, CREATE ON SCHEMA public TO "${POSTGRES_USER}";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "${POSTGRES_USER}";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "${POSTGRES_USER}";

-- Create ENUM types
CREATE TYPE relationship_status_enum AS ENUM ('pending', 'accepted', 'rejected', 'blocked');
CREATE TYPE progress_status_enum AS ENUM ('not_started', 'in_progress', 'finished');