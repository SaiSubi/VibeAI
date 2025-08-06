-- Add spotify_registered column to tokens table
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS spotify_registered BOOLEAN DEFAULT TRUE;

-- Update all existing users to have spotify_registered = TRUE
UPDATE tokens SET spotify_registered = TRUE WHERE spotify_registered IS NULL OR spotify_registered = FALSE; 