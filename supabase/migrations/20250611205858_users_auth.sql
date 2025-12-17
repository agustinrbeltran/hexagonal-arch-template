-- Create enum type for user roles
CREATE TYPE userrole AS ENUM ('SUPER_ADMIN', 'ADMIN', 'USER');

-- Create auth_sessions table
CREATE TABLE auth_sessions (
    id TEXT NOT NULL,
    user_id UUID NOT NULL,
    expiration TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

-- Create users table
CREATE TABLE users (
    id UUID NOT NULL,
    username VARCHAR(20) NOT NULL,
    password_hash BYTEA NOT NULL,
    role userrole NOT NULL,
    is_active BOOLEAN NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username)
);
