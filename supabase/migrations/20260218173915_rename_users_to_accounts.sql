-- Rename the enum type
ALTER TYPE userrole RENAME TO accountrole;

-- Rename the table
ALTER TABLE users RENAME TO accounts;

-- Rename the username column to email and expand to VARCHAR(255)
ALTER TABLE accounts RENAME COLUMN username TO email;
ALTER TABLE accounts ALTER COLUMN email TYPE VARCHAR(255);
