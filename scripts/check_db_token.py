#!/usr/bin/env python3
"""
Check the token in the database
"""

import psycopg2
from utils.config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_db_token():
    """Check the token stored in the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get token info for your user
        cursor.execute("""
            SELECT user_id, user_name, access_token, expires_at
            FROM tokens 
            WHERE user_id = '31r4bejefnssdwtcfgw6kf3niv4i'
        """)
        
        result = cursor.fetchone()
        if result:
            user_id, user_name, access_token, expires_at = result
            print(f"👤 User: {user_name}")
            print(f"🆔 User ID: {user_id}")
            print(f"⏰ Expires: {expires_at}")
            print(f"🔑 Token (first 20 chars): {access_token[:20]}...")
        else:
            print("❌ No token found for user")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db_token() 