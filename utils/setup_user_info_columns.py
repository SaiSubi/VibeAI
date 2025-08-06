#!/usr/bin/env python3
"""
Script to add user info columns to the database
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import DATABASE_URL
import psycopg2

def setup_user_info_columns():
    """
    Add user_name and user_email columns to the tokens table
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Add columns
        cur.execute("ALTER TABLE tokens ADD COLUMN IF NOT EXISTS user_name TEXT;")
        cur.execute("ALTER TABLE tokens ADD COLUMN IF NOT EXISTS user_email TEXT;")
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tokens_user_name ON tokens(user_name);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tokens_user_email ON tokens(user_email);")
        
        conn.commit()
        print("✅ Successfully added user_name and user_email columns to tokens table")
        
    except Exception as e:
        print(f"❌ Error setting up columns: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_user_info_columns() 