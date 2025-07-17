CREATE DATABASE mapa_test;
\connect mapa_test
CREATE EXTENSION postgis;

-- Create user
CREATE USER mapa WITH PASSWORD '12345Abc.';

-- Grant superuser privileges (same as postgres)
-- ALTER USER mapa WITH SUPERUSER;

-- (Optional) Grant all privileges on existing database `mapa_test`
-- GRANT ALL PRIVILEGES ON DATABASE mapa_test TO mapa;
