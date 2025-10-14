#!/usr/bin/env python3
"""
Test Database Migration Script: Migrate only 10 songs first
"""

import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_migration():
    """Test migration with just 10 songs"""
    sqlite_path = "song_database.db"
    postgres_url = os.getenv("DATABASE_URL")
    
    print("🧪 Testing migration with 10 songs...")
    print("=" * 50)
    
    # Connect to databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    postgres_conn = psycopg2.connect(postgres_url)
    
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()
    
    # Drop and recreate PostgreSQL table
    print("Step 1: Creating PostgreSQL schema...")
    postgres_cursor.execute("DROP TABLE IF EXISTS songs CASCADE;")
    postgres_cursor.execute('''
        CREATE TABLE songs (
            id SERIAL PRIMARY KEY,
            spotify_id TEXT UNIQUE,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            release_year INTEGER,
            duration_ms INTEGER,
            popularity INTEGER,
            valence REAL,
            energy REAL,
            danceability REAL,
            acousticness REAL,
            instrumentalness REAL,
            liveness REAL,
            loudness REAL,
            speechiness REAL,
            tempo REAL,
            key INTEGER,
            mode INTEGER,
            time_signature INTEGER,
            lyrical_themes TEXT,
            mood_tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            energy_level INTEGER,
            popularity_score INTEGER,
            language TEXT,
            danceability_score INTEGER,
            melodic_expressiveness INTEGER,
            vocal_prominence INTEGER,
            song_description TEXT,
            timbre INTEGER,
            theme_scores TEXT,
            last_analyzed TEXT,
            genre TEXT,
            vector_embedding TEXT
        );
    ''')
    postgres_conn.commit()
    print("✅ PostgreSQL schema created")
    
    # Get 10 songs from SQLite
    print("\nStep 2: Fetching 10 songs from SQLite...")
    sqlite_cursor.execute("""
        SELECT spotify_id, title, artist, album, release_year, duration_ms, 
               popularity, valence, energy, danceability, acousticness,
               instrumentalness, liveness, loudness, speechiness, tempo,
               key, mode, time_signature, lyrical_themes, mood_tags,
               created_at, energy_level, popularity_score, language,
               danceability_score, melodic_expressiveness, vocal_prominence,
               song_description, timbre, theme_scores, last_analyzed,
               genre, vector_embedding 
        FROM songs LIMIT 10
    """)
    
    songs = sqlite_cursor.fetchall()
    print(f"📊 Found {len(songs)} songs to migrate")
    
    # Show sample songs
    print("\n🎵 Sample songs to migrate:")
    for i, song in enumerate(songs[:3]):
        print(f"  {i+1}. {song[1]} by {song[2]}")
    
    # Migrate songs
    print("\nStep 3: Migrating songs...")
    migrated_count = 0
    
    insert_query = """
        INSERT INTO songs (spotify_id, title, artist, album, release_year, duration_ms,
                          popularity, valence, energy, danceability, acousticness,
                          instrumentalness, liveness, loudness, speechiness, tempo,
                          key, mode, time_signature, lyrical_themes, mood_tags,
                          created_at, energy_level, popularity_score, language,
                          danceability_score, melodic_expressiveness, vocal_prominence,
                          song_description, timbre, theme_scores, last_analyzed,
                          genre, vector_embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for song in songs:
        try:
            # Convert None values and empty strings
            song_data = []
            for value in song:
                if value is None or (isinstance(value, str) and value == ''):
                    song_data.append(None)
                else:
                    song_data.append(value)
            
            postgres_cursor.execute(insert_query, song_data)
            migrated_count += 1
            print(f"✅ Migrated: {song[1]} by {song[2]}")
            
        except Exception as e:
            print(f"❌ Error migrating {song[1]}: {e}")
    
    postgres_conn.commit()
    
    # Verify migration
    print(f"\nStep 4: Verifying migration...")
    postgres_cursor.execute("SELECT COUNT(*) FROM songs")
    count = postgres_cursor.fetchone()[0]
    
    postgres_cursor.execute("SELECT title, artist, genre FROM songs ORDER BY id LIMIT 5")
    migrated_songs = postgres_cursor.fetchall()
    
    print(f"📊 PostgreSQL now contains {count} songs")
    print("🎵 Migrated songs:")
    for song in migrated_songs:
        print(f"  - {song[0]} by {song[1]} ({song[2]})")
    
    # Clean up
    sqlite_conn.close()
    postgres_conn.close()
    
    if migrated_count == count:
        print(f"\n🎉 Test migration successful!")
        print(f"📊 {migrated_count} songs migrated successfully")
        return True
    else:
        print(f"\n⚠️  Migration completed with discrepancies")
        print(f"📊 Expected: {migrated_count}, Actual: {count}")
        return False

if __name__ == "__main__":
    success = test_migration()
    if success:
        print("\n✅ Ready to run full migration!")
    else:
        print("\n❌ Test failed - need to fix issues first")
