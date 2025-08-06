-- Add user info columns to tokens table
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS user_name TEXT;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS user_email TEXT;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_tokens_user_name ON tokens(user_name);
CREATE INDEX IF NOT EXISTS idx_tokens_user_email ON tokens(user_email); 