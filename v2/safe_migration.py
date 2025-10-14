#!/usr/bin/env python3
"""
Duplicate-Safe Database Migration Script: SQLite to PostgreSQL
Handles duplicate songs by keeping only the first occurrence
"""

import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def safe_migration():
    """Migration that handles duplicates safely"""
    sqlite_path = "song_database.db"
    postgres_url = os.getenv("DATABASE_URL")
    
    print("🛡️  Starting duplicate-safe migration...")
    print("=" * 60)
    
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
    
    # Check for duplicates in SQLite
    print("\nStep 2: Checking for duplicates...")
    sqlite_cursor.execute("""
        SELECT spotify_id, COUNT(*) as count 
        FROM songs 
        WHERE spotify_id IS NOT NULL 
        GROUP BY spotify_id 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    duplicates = sqlite_cursor.fetchall()
    
    if duplicates:
        print(f"⚠️  Found {len(duplicates)} duplicate spotify_ids:")
        for spotify_id, count in duplicates[:5]:
            print(f"  - {spotify_id}: {count} copies")
    else:
        print("✅ No duplicates found")
    
    # Get total count
    sqlite_cursor.execute("SELECT COUNT(*) FROM songs")
    total_songs = sqlite_cursor.fetchone()[0]
    print(f"📊 Total songs in SQLite: {total_songs}")
    
    # Migrate songs with duplicate handling
    print("\nStep 3: Migrating songs (handling duplicates)...")
    
    # Get unique songs by using GROUP BY to keep first occurrence
    sqlite_cursor.execute("""
        SELECT spotify_id, title, artist, album, release_year, duration_ms, 
               popularity, valence, energy, danceability, acousticness,
               instrumentalness, liveness, loudness, speechiness, tempo,
               key, mode, time_signature, lyrical_themes, mood_tags,
               created_at, energy_level, popularity_score, language,
               danceability_score, melodic_expressiveness, vocal_prominence,
               song_description, timbre, theme_scores, last_analyzed,
               genre, vector_embedding 
        FROM songs 
        WHERE spotify_id IS NOT NULL
        GROUP BY spotify_id
        ORDER BY MIN(id)
    """)
    
    songs = sqlite_cursor.fetchall()
    print(f"📊 Unique songs to migrate: {len(songs)}")
    
    # Show sample songs
    print("\n🎵 Sample songs to migrate:")
    for i, song in enumerate(songs[:3]):
        print(f"  {i+1}. {song[1]} by {song[2]}")
    
    # Migrate songs in batches
    batch_size = 100
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
        ON CONFLICT (spotify_id) DO NOTHING
    """
    
    for i in range(0, len(songs), batch_size):
        batch = songs[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"🔄 Processing batch {batch_num} (songs {i+1}-{min(i+batch_size, len(songs))})")
        
        batch_migrated = 0
        for song in batch:
            try:
                # Convert None values and empty strings
                song_data = []
                for value in song:
                    if value is None or (isinstance(value, str) and value == ''):
                        song_data.append(None)
                    else:
                        song_data.append(value)
                
                postgres_cursor.execute(insert_query, song_data)
                batch_migrated += 1
                
            except Exception as e:
                print(f"❌ Error migrating {song[1]}: {e}")
        
        postgres_conn.commit()
        migrated_count += batch_migrated
        print(f"✅ Migrated {batch_migrated} songs in this batch (Total: {migrated_count}/{len(songs)})")
    
    # Verify migration
    print(f"\nStep 4: Verifying migration...")
    postgres_cursor.execute("SELECT COUNT(*) FROM songs")
    count = postgres_cursor.fetchone()[0]
    
    postgres_cursor.execute("SELECT title, artist, genre FROM songs ORDER BY id LIMIT 5")
    migrated_songs = postgres_cursor.fetchall()
    
    print(f"📊 PostgreSQL now contains {count} songs")
    print("🎵 Sample migrated songs:")
    for song in migrated_songs:
        print(f"  - {song[0]} by {song[1]} ({song[2]})")
    
    # Clean up
    sqlite_conn.close()
    postgres_conn.close()
    
    print(f"\n🎉 Migration completed!")
    print(f"📊 {migrated_count} unique songs migrated successfully")
    print(f"📊 {total_songs - migrated_count} duplicates were skipped")
    
    return True

if __name__ == "__main__":
    success = safe_migration()
    if success:
        print("\n✅ Database migration completed successfully!")
    else:
        print("\n❌ Migration failed")
