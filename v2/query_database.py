#!/usr/bin/env python3
"""
Query and explore the song database
"""

import sqlite3
import json
from typing import List, Dict

class SongDatabaseQuery:
    def __init__(self, db_path: str = "song_database.db"):
        self.db_path = db_path
    
    def get_all_songs(self, limit: int = 10) -> List[Dict]:
        """Get all songs with basic info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, album, release_year, valence, energy, danceability
            FROM songs
            ORDER BY title
            LIMIT ?
        """, (limit,))
        
        songs = []
        for row in cursor.fetchall():
            songs.append({
                "title": row[0],
                "artist": row[1],
                "album": row[2],
                "release_year": row[3],
                "valence": row[4],
                "energy": row[5],
                "danceability": row[6]
            })
        
        conn.close()
        return songs
    
    def search_by_mood(self, min_valence: float = 0.7, min_energy: float = 0.7) -> List[Dict]:
        """Find upbeat/happy songs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, album, valence, energy, danceability
            FROM songs
            WHERE valence >= ? AND energy >= ?
            ORDER BY (valence + energy) DESC
            LIMIT 10
        """, (min_valence, min_energy))
        
        songs = []
        for row in cursor.fetchall():
            songs.append({
                "title": row[0],
                "artist": row[1],
                "album": row[2],
                "valence": row[3],
                "energy": row[4],
                "danceability": row[5]
            })
        
        conn.close()
        return songs
    
    def search_by_artist(self, artist_name: str) -> List[Dict]:
        """Find songs by a specific artist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, album, release_year, valence, energy
            FROM songs
            WHERE LOWER(artist) LIKE LOWER(?)
            ORDER BY release_year DESC
        """, (f"%{artist_name}%",))
        
        songs = []
        for row in cursor.fetchall():
            songs.append({
                "title": row[0],
                "artist": row[1],
                "album": row[2],
                "release_year": row[3],
                "valence": row[4],
                "energy": row[5]
            })
        
        conn.close()
        return songs
    
    def get_lyrical_themes(self, song_title: str) -> Dict:
        """Get lyrical themes for a specific song"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, lyrical_themes
            FROM songs
            WHERE LOWER(title) LIKE LOWER(?)
            LIMIT 1
        """, (f"%{song_title}%",))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                themes = json.loads(row[2]) if row[2] else {}
                return {
                    "title": row[0],
                    "artist": row[1],
                    "themes": themes
                }
            except json.JSONDecodeError:
                return {
                    "title": row[0],
                    "artist": row[1],
                    "themes": {"error": "Invalid JSON"}
                }
        return None
    
    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT artist) FROM songs")
        unique_artists = cursor.fetchone()[0]
        
        # Year range
        cursor.execute("""
            SELECT MIN(release_year), MAX(release_year)
            FROM songs
            WHERE release_year IS NOT NULL
        """)
        year_range = cursor.fetchone()
        
        # Feature ranges
        cursor.execute("""
            SELECT 
                MIN(valence), MAX(valence), AVG(valence),
                MIN(energy), MAX(energy), AVG(energy),
                MIN(danceability), MAX(danceability), AVG(danceability)
            FROM songs
        """)
        feature_stats = cursor.fetchone()
        
        # Top artists
        cursor.execute("""
            SELECT artist, COUNT(*) as song_count
            FROM songs
            GROUP BY artist
            ORDER BY song_count DESC
            LIMIT 5
        """)
        top_artists = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_songs": total_songs,
            "unique_artists": unique_artists,
            "year_range": {
                "min": year_range[0] if year_range[0] else None,
                "max": year_range[1] if year_range[1] else None
            },
            "feature_stats": {
                "valence": {"min": feature_stats[0], "max": feature_stats[1], "avg": feature_stats[2]},
                "energy": {"min": feature_stats[3], "max": feature_stats[4], "avg": feature_stats[5]},
                "danceability": {"min": feature_stats[6], "max": feature_stats[7], "avg": feature_stats[8]}
            },
            "top_artists": [{"artist": artist, "count": count} for artist, count in top_artists]
        }

def main():
    """Main function to explore the database"""
    print("🔍 VibeAI v2 - Database Explorer")
    print("=" * 40)
    
    query = SongDatabaseQuery()
    
    # Get database stats
    stats = query.get_database_stats()
    
    print(f"\n📊 Database Overview:")
    print(f"Total songs: {stats['total_songs']}")
    print(f"Unique artists: {stats['unique_artists']}")
    
    if stats['year_range']['min']:
        print(f"Year range: {stats['year_range']['min']} - {stats['year_range']['max']}")
    
    print(f"\n🎵 Top Artists:")
    for artist_info in stats['top_artists']:
        print(f"  - {artist_info['artist']}: {artist_info['count']} songs")
    
    print(f"\n📈 Feature Averages:")
    if stats['feature_stats']['valence']['avg'] is not None:
        print(f"  Valence: {stats['feature_stats']['valence']['avg']:.3f}")
    if stats['feature_stats']['energy']['avg'] is not None:
        print(f"  Energy: {stats['feature_stats']['energy']['avg']:.3f}")
    if stats['feature_stats']['danceability']['avg'] is not None:
        print(f"  Danceability: {stats['feature_stats']['danceability']['avg']:.3f}")
    
    # Show some upbeat songs (only if we have audio features)
    if stats['feature_stats']['valence']['avg'] is not None:
        print(f"\n🎉 Upbeat Songs (valence & energy > 0.7):")
        upbeat_songs = query.search_by_mood()
        for song in upbeat_songs[:5]:
            print(f"  - {song['title']} by {song['artist']} (V: {song['valence']:.2f}, E: {song['energy']:.2f})")
    else:
        print(f"\n🎉 Upbeat Songs: Audio features not available (403 error)")
    
    # Show some sample songs
    print(f"\n🎵 Sample Songs:")
    sample_songs = query.get_all_songs(5)
    for song in sample_songs:
        print(f"  - {song['title']} by {song['artist']} ({song['album']}, {song['release_year']})")

if __name__ == "__main__":
    main() 