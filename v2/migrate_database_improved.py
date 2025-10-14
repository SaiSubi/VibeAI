#!/usr/bin/env python3
"""
Improved Database Migration Script: SQLite to PostgreSQL
Migrates VibeAI v2 song database from SQLite to PostgreSQL (Neon) with batch processing
"""

import sqlite3
import psycopg2
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ImprovedDatabaseMigrator:
    def __init__(self):
        self.sqlite_path = "song_database.db"
        self.postgres_url = os.getenv("DATABASE_URL")
        self.batch_size = 100  # Process songs in batches
        
    def get_sqlite_connection(self):
        """Get SQLite connection"""
        return sqlite3.connect(self.sqlite_path)
    
    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.postgres_url)
    
    def create_postgres_schema(self):
        """Create PostgreSQL schema for songs table"""
        conn = self.get_postgres_connection()
        cursor = conn.cursor()
        
        # Drop table if exists
        cursor.execute("DROP TABLE IF EXISTS songs CASCADE;")
        
        # Create songs table with PostgreSQL-compatible schema
        cursor.execute('''
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
                energy_level REAL DEFAULT 0,
                popularity_score INTEGER DEFAULT 0,
                language TEXT DEFAULT 'Unknown',
                danceability_score INTEGER DEFAULT 0,
                melodic_expressiveness INTEGER DEFAULT 0,
                vocal_prominence INTEGER DEFAULT 0,
                song_description TEXT DEFAULT '',
                timbre INTEGER DEFAULT 0,
                theme_scores TEXT DEFAULT '{}',
                last_analyzed TEXT,
                genre TEXT DEFAULT 'Unknown',
                vector_embedding TEXT DEFAULT NULL
            );
        ''')
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_spotify_id ON songs(spotify_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_language ON songs(language);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_energy_level ON songs(energy_level);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_popularity_score ON songs(popularity_score);")
        
        conn.commit()
        conn.close()
        print("✅ PostgreSQL schema created successfully")
    
    def migrate_data_batch(self):
        """Migrate data from SQLite to PostgreSQL in batches"""
        sqlite_conn = self.get_sqlite_connection()
        postgres_conn = self.get_postgres_connection()
        
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get total count
        sqlite_cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = sqlite_cursor.fetchone()[0]
        print(f"📊 Total songs to migrate: {total_songs}")
        
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        insert_query = f"INSERT INTO songs ({columns}) VALUES ({placeholders})"
        
        # Process in batches
        offset = 0
        migrated_count = 0
        
        while offset < total_songs:
            print(f"🔄 Processing batch {offset//self.batch_size + 1} (songs {offset+1}-{min(offset+self.batch_size, total_songs)})")
            
            # Get batch of songs
            sqlite_cursor.execute(f"SELECT * FROM songs LIMIT {self.batch_size} OFFSET {offset}")
            songs_batch = sqlite_cursor.fetchall()
            
            if not songs_batch:
                break
            
            # Migrate batch
            batch_migrated = 0
            for song in songs_batch:
                try:
                    # Convert song data to tuple, handling None values
                    song_data = []
                    for value in song:
                        if value is None:
                            song_data.append(None)
                        elif isinstance(value, str) and value == '':
                            song_data.append(None)
                        else:
                            song_data.append(value)
                    
                    postgres_cursor.execute(insert_query, song_data)
                    batch_migrated += 1
                    
                except Exception as e:
                    print(f"❌ Error migrating song {song[0]}: {e}")
                    continue
            
            # Commit batch
            postgres_conn.commit()
            migrated_count += batch_migrated
            
            print(f"✅ Migrated {batch_migrated} songs in this batch (Total: {migrated_count}/{total_songs})")
            
            offset += self.batch_size
        
        sqlite_conn.close()
        postgres_conn.close()
        
        print(f"🎉 Migration completed! Migrated {migrated_count} songs to PostgreSQL")
        return migrated_count
    
    def verify_migration(self):
        """Verify the migration was successful"""
        postgres_conn = self.get_postgres_connection()
        postgres_cursor = postgres_conn.cursor()
        
        # Count songs
        postgres_cursor.execute("SELECT COUNT(*) FROM songs")
        count = postgres_cursor.fetchone()[0]
        
        # Get sample data
        postgres_cursor.execute("SELECT id, title, artist, genre, language FROM songs ORDER BY id LIMIT 5")
        sample_songs = postgres_cursor.fetchall()
        
        postgres_conn.close()
        
        print(f"📊 PostgreSQL now contains {count} songs")
        print("🎵 Sample songs:")
        for song in sample_songs:
            print(f"  - {song[1]} by {song[2]} ({song[3]}, {song[4]})")
        
        return count
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting improved SQLite to PostgreSQL migration...")
        print("=" * 60)
        
        try:
            # Step 1: Create PostgreSQL schema
            print("Step 1: Creating PostgreSQL schema...")
            self.create_postgres_schema()
            
            # Step 2: Migrate data in batches
            print("\nStep 2: Migrating data in batches...")
            migrated_count = self.migrate_data_batch()
            
            # Step 3: Verify migration
            print("\nStep 3: Verifying migration...")
            final_count = self.verify_migration()
            
            if migrated_count == final_count:
                print(f"\n🎉 Migration completed successfully!")
                print(f"📊 {final_count} songs migrated to PostgreSQL")
            else:
                print(f"\n⚠️  Migration completed with discrepancies")
                print(f"📊 Expected: {migrated_count}, Actual: {final_count}")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

def main():
    """Main migration function"""
    migrator = ImprovedDatabaseMigrator()
    
    # Check if DATABASE_URL is set
    if not migrator.postgres_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set your Neon PostgreSQL connection string")
        return
    
    # Check if SQLite database exists
    if not os.path.exists(migrator.sqlite_path):
        print(f"❌ SQLite database not found: {migrator.sqlite_path}")
        return
    
    migrator.run_migration()

if __name__ == "__main__":
    main()
