#!/usr/bin/env python3
"""
Small test script to verify the database builder works correctly
"""

from test import SongDatabaseBuilder
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_small_database():
    """Test the database builder with a small subset"""
    print("🧪 Testing VibeAI v2 Database Builder")
    print("=" * 40)
    
    # Initialize builder
    builder = SongDatabaseBuilder("test_song_database.db")
    
    # Test with specific playlist names (you can modify these)
    test_playlist_names = [
        # Add 1-2 playlist names here for testing
        # "My Favorites",
        # "Workout Mix"
    ]
    
    try:
        # Build database with limited playlists
        builder.build_database_from_playlists(playlist_names=test_playlist_names)
        
        # Get and display stats
        stats = builder.get_database_stats()
        
        print("\n📊 Test Database Statistics:")
        print(f"Total songs: {stats['total_songs']}")
        print(f"Unique artists: {stats['unique_artists']}")
        
        if stats['total_songs'] > 0:
            print(f"Average valence: {stats['average_features']['valence']:.3f}")
            print(f"Average energy: {stats['average_features']['energy']:.3f}")
            print(f"Average danceability: {stats['average_features']['danceability']:.3f}")
            
            # Show some sample songs
            print("\n🎵 Sample songs in database:")
            conn = builder.db_path
            import sqlite3
            db_conn = sqlite3.connect(conn)
            cursor = db_conn.cursor()
            cursor.execute("SELECT title, artist, album, release_year FROM songs LIMIT 5")
            samples = cursor.fetchall()
            for title, artist, album, year in samples:
                print(f"  - {title} by {artist} ({album}, {year})")
            db_conn.close()
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_small_database() 