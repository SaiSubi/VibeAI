#!/usr/bin/env python3
"""
Check what users are in the database
"""

import psycopg2
from utils.config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_users():
    """Check what users are in the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT user_id, user_name, user_email, spotify_registered FROM tokens")
        users = cursor.fetchall()
        
        print("👥 Users in database:")
        for user_id, user_name, user_email, spotify_registered in users:
            print(f"  - User ID: {user_id}")
            print(f"    Name: {user_name}")
            print(f"    Email: {user_email}")
            print(f"    Spotify Registered: {spotify_registered}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_users() 