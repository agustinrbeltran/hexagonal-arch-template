-- Step 1: Remove existing profile and outbox data that references old accounts
DELETE FROM public.profiles;
DELETE FROM public.outbox;

-- Step 2: Drop profiles FK to accounts (will be re-added to auth.users)
ALTER TABLE public.profiles DROP CONSTRAINT profiles_account_id_fkey;

-- Step 3: Create account_metadata table
CREATE TABLE public.account_metadata (
    account_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role accountrole NOT NULL DEFAULT 'USER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Step 4: Add profiles FK to auth.users
ALTER TABLE public.profiles
    ADD CONSTRAINT profiles_account_id_fkey
        FOREIGN KEY (account_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Step 5: Drop refresh_tokens table
DROP TABLE public.refresh_tokens;

-- Step 6: Drop accounts table
DROP TABLE public.accounts;
