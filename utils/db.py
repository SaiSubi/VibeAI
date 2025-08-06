

import os
import psycopg2  
from datetime import datetime
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def save_tokens_to_db(user_id, access_token, refresh_token, expires_at, user_name=None, user_email=None):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tokens (user_id, access_token, refresh_token, expires_at, spotify_registered, user_name, user_email)
        VALUES (%s, %s, %s, %s, TRUE, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            expires_at = EXCLUDED.expires_at,
            spotify_registered = TRUE,
            user_name = COALESCE(EXCLUDED.user_name, tokens.user_name),
            user_email = COALESCE(EXCLUDED.user_email, tokens.user_email);
    """, (user_id, access_token, refresh_token, expires_at, user_name, user_email))

    conn.commit()
    cur.close()
    conn.close()

def get_tokens_for_user(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM tokens WHERE user_id = %s", (user_id,))
    token_row = cur.fetchone()

    cur.close()
    conn.close()

    if not token_row:
        raise Exception("❌ No tokens found for user")

    return token_row

def check_user_registered(user_id):
    """
    Check if a user is registered with Spotify (has valid tokens)
    Returns True if user exists and has valid tokens, False otherwise
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT spotify_registered, access_token, refresh_token 
        FROM tokens 
        WHERE user_id = %s
    """, (user_id,))
    
    result = cur.fetchone()
    
    cur.close()
    conn.close()

    if result:
        spotify_registered, access_token, refresh_token = result
        # User is registered if they have the flag AND valid tokens
        return spotify_registered and access_token is not None and refresh_token is not None
    return False

def get_users_without_info():
    """
    Get all users who have tokens but missing name or email
    Returns list of user_ids
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, access_token 
        FROM tokens 
        WHERE (user_name IS NULL OR user_email IS NULL) 
        AND access_token IS NOT NULL
    """)
    
    results = cur.fetchall()
    
    cur.close()
    conn.close()

    return results

def update_user_info(user_id, user_name, user_email):
    """
    Update user name and email for a specific user
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        UPDATE tokens 
        SET user_name = %s, user_email = %s
        WHERE user_id = %s
    """, (user_name, user_email, user_id))

    conn.commit()
    cur.close()
    conn.close()

def logout_user_from_db(user_id):
    """
    Removes user tokens from database (logout functionality)
    Returns True if user was found and tokens were cleared, False otherwise
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT logout_user(%s)", (user_id,))
    result = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return result