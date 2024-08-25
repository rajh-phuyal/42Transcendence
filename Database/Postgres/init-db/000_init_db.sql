--  This script is used to create the transcendence schema in the "postgres" database
\c postgres

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS transcendence;

-- Grant privileges on the public schema to admin
GRANT USAGE, CREATE ON SCHEMA transcendence TO "admin";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA transcendence TO "admin";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA transcendence TO "admin";

-- Create ENUM types
CREATE TYPE transcendence.relationship_status_enum AS ENUM ('pending' , 'accepted', 'rejected', 'blocked');
CREATE TYPE transcendence.progress_status_enum AS ENUM ('not_started', 'in_progress', 'finished');