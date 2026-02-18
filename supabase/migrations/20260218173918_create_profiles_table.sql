CREATE TABLE profiles (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL UNIQUE REFERENCES accounts(id),
    username VARCHAR(20) UNIQUE
);
