-- Function to remove user tokens (logout functionality)
-- This function clears the access_token and refresh_token but keeps the user_id for potential future use
CREATE OR REPLACE FUNCTION logout_user(user_id_param TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tokens 
    SET access_token = NULL, 
        refresh_token = NULL, 
        expires_at = NULL
    WHERE user_id = user_id_param;
    
    -- Return true if a row was affected (user existed), false otherwise
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql; 