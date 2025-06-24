-- Initial database setup for GAP Quotes service
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create application user (if not using default user)
-- Note: The POSTGRES_USER from docker-compose.yml will be the main user

-- Set default privileges for the application
GRANT ALL PRIVILEGES ON DATABASE gap_quotes TO gap_user;

-- Ensure proper encoding
SET client_encoding = 'UTF8';