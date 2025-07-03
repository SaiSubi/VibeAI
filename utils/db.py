

import os
import psycopg2  
from datetime import datetime
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def save_tokens_to_db(user_id, access_token, refresh_token, expires_at):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tokens (user_id, access_token, refresh_token, expires_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            expires_at = EXCLUDED.expires_at;
    """, (user_id, access_token, refresh_token, expires_at))

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