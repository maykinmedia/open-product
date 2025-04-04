CREATE USER openproduct;
CREATE DATABASE openproduct;
GRANT ALL PRIVILEGES ON DATABASE openproduct TO openproduct;
-- Needed to create a test db locally.
ALTER USER openproduct SUPERUSER;
-- On Postgres 15+, connect to the database and grant schema permissions.
-- GRANT USAGE, CREATE ON SCHEMA public TO openforms;
