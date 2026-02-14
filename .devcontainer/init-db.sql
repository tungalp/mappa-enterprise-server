-- 1. Only create if it doesn't exist (or just skip since Docker creates it for you)
-- CREATE DATABASE mapa_test; 

-- 2. Switch to the DB (this is safe)
\connect mapa_test

-- 3. Only create the extension if it's not there
CREATE EXTENSION IF NOT EXISTS postgis;

-- 4. Create the user safely
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'mapa') THEN
        CREATE USER mapa WITH PASSWORD '12345Abc.';
    END IF;
END
$$;

-- 5. These are safe to run multiple times
ALTER USER mapa WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE mapa_test TO mapa;