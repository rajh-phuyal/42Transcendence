DO $$ 
BEGIN 
    BEGIN
        CREATE ROLE "user" WITH LOGIN NOSUPERUSER INHERIT CREATEDB CREATEROLE NOREPLICATION;
    EXCEPTION WHEN duplicate_object THEN 
        RAISE NOTICE 'Role "user" already exists, skipping creation';
    END;

    EXECUTE format('ALTER USER "user" WITH PASSWORD %L', 'user123');

    CREATE SCHEMA IF NOT EXISTS public;
    GRANT USAGE, CREATE, SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "user";
    GRANT USAGE, CREATE ON SCHEMA public TO "user";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "user";

    GRANT CREATE, TEMPORARY ON DATABASE "transcendece" TO "user";

    COMMENT ON ROLE "user" IS 'general purpose user';

EXCEPTION 
    WHEN OTHERS THEN 
        RAISE NOTICE 'An error occurred: %', SQLERRM;
        RAISE NOTICE 'Error code: %', SQLSTATE;
END $$;