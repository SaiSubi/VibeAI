#!/usr/bin/env python3
"""
VibeAI v2 - Enhanced Song Database Builder
This script creates a comprehensive database of songs with Spotify features
and prepares for LLM-based lyrical analysis.
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from dotenv import load_dotenv

# Import existing utilities
from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, VibeAI_userid
from utils.token import get_access_token
# from utils.groq import call_groq_api  # Commented out for now

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SongDatabaseBuilder:
    def __init__(self, db_path: str = "song_database.db"):
        self.db_path = db_path
        self.access_token = None
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with the songs table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def get_access_token_for_user(self, user_id: str = None) -> str:
        """Get Spotify access token for the specified user or service account"""
        try:
            if user_id:
                self.access_token = get_access_token(user_id)
            else:
                # Use service account (which should be your personal account)
                self.access_token = get_access_token(VibeAI_userid)
            
            logger.info("✅ Access token obtained")
            return self.access_token
        except Exception as e:
            logger.error(f"❌ Failed to get access token: {e}")
            raise
    
    def get_user_playlists(self, user_id: str = None) -> List[Dict]:
        """Get all playlists for the user"""
        if not self.access_token:
            self.get_access_token_for_user(user_id)
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # First get the current user's ID
        me_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            current_user_id = user_data["id"]
            display_name = user_data.get("display_name", "Unknown")
            logger.info(f"🔍 Current user: {display_name} (ID: {current_user_id})")
        else:
            current_user_id = user_id or VibeAI_userid
            logger.warning(f"⚠️ Could not get current user ID, using: {current_user_id}")
        
        url = f"https://api.spotify.com/v1/users/{current_user_id}/playlists"
        
        playlists = []
        offset = 0
        limit = 50
        
        while True:
            params = {"limit": limit, "offset": offset}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get playlists: {response.status_code}")
                logger.error(f"❌ Response: {response.text}")
                break
            
            data = response.json()
            playlists.extend(data.get("items", []))
            
            if len(data.get("items", [])) < limit:
                break
            
            offset += limit
        
        logger.info(f"✅ Found {len(playlists)} playlists")
        return playlists
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get all tracks from a specific playlist"""
        if not self.access_token:
            raise Exception("Access token not available")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        
        tracks = []
        offset = 0
        limit = 100
        
        while True:
            params = {"limit": limit, "offset": offset}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get playlist tracks: {response.status_code}")
                break
            
            data = response.json()
            playlist_tracks = data.get("items", [])
            
            # Extract track data from playlist items
            for item in playlist_tracks:
                if item.get("track") and item["track"].get("id"):
                    tracks.append(item["track"])
            
            if len(playlist_tracks) < limit:
                break
            
            offset += limit
        
        logger.info(f"✅ Found {len(tracks)} tracks in playlist")
        return tracks
    
    def get_audio_features(self, track_ids: List[str]) -> Dict[str, Dict]:
        """Get audio features for multiple tracks"""
        if not self.access_token:
            raise Exception("Access token not available")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = "https://api.spotify.com/v1/audio-features"
        
        # Spotify API allows max 100 tracks per request
        features = {}
        
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            params = {"ids": ",".join(batch)}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for track_features in data.get("audio_features", []):
                    if track_features:
                        features[track_features["id"]] = track_features
            else:
                logger.error(f"❌ Failed to get audio features: {response.status_code}")
        
        logger.info(f"✅ Retrieved audio features for {len(features)} tracks")
        return features
    
    # def analyze_lyrical_themes(self, song_title: str, artist: str) -> str:
    #     """Use Groq to analyze lyrical themes of a song"""
    #     prompt = f"""
    #     Analyze the lyrical themes and mood of the song "{song_title}" by {artist}.
    #     
    #     Consider:
    #     - Emotional themes (love, heartbreak, joy, sadness, etc.)
    #     - Musical mood (upbeat, melancholic, energetic, calm, etc.)
    #     - Cultural context
    #     - Target audience
    #     
    #     Return a JSON object with these fields:
    #     {{
    #         "themes": ["theme1", "theme2", "theme3"],
    #         "mood": "primary_mood",
    #         "energy_level": "high/medium/low",
    #         "cultural_context": "description",
    #         "target_audience": "description"
    #     }}
    #     
    #     Keep the response concise and focused on the most relevant themes.
    #     """
    #     
    #     try:
    #         response = call_groq_api(prompt)
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         logger.error(f"❌ Failed to analyze lyrical themes for {song_title}: {e}")
    #         return json.dumps({
    #             "themes": ["unknown"],
    #             "mood": "unknown",
    #             "energy_level": "unknown",
    #             "cultural_context": "unknown",
    #             "target_audience": "unknown"
    #         })
    
    def save_song_to_db(self, track: Dict, audio_features: Dict = None, lyrical_analysis: str = None):
        """Save a song with all its features to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract basic track info
            spotify_id = track.get("id")
            title = track.get("name", "Unknown")
            artist = track.get("artists", [{}])[0].get("name", "Unknown")
            album = track.get("album", {}).get("name", "Unknown")
            release_date = track.get("album", {}).get("release_date", "")
            duration_ms = track.get("duration_ms", 0)
            popularity = track.get("popularity", 0)
            
            # Parse release year
            release_year = None
            if release_date:
                try:
                    release_year = int(release_date[:4])
                except ValueError:
                    pass
            
            # Extract audio features
            features = audio_features.get(spotify_id, {}) if audio_features else {}
            
            # Prepare lyrical analysis (commented out for now)
            # if not lyrical_analysis:
            #     lyrical_analysis = self.analyze_lyrical_themes(title, artist)
            lyrical_analysis = None  # Will be added later via ChatGPT analysis
            
            cursor.execute('''
                INSERT OR REPLACE INTO songs (
                    spotify_id, title, artist, album, release_year, duration_ms, popularity,
                    valence, energy, danceability, acousticness, instrumentalness,
                    liveness, loudness, speechiness, tempo, key, mode, time_signature,
                    lyrical_themes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                spotify_id, title, artist, album, release_year, duration_ms, popularity,
                features.get("valence"), features.get("energy"), features.get("danceability"),
                features.get("acousticness"), features.get("instrumentalness"),
                features.get("liveness"), features.get("loudness"), features.get("speechiness"),
                features.get("tempo"), features.get("key"), features.get("mode"),
                features.get("time_signature"), lyrical_analysis
            ))
            
            conn.commit()
            logger.info(f"✅ Saved song: {title} by {artist}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save song {title}: {e}")
        finally:
            conn.close()
    
    def build_database_from_playlists(self, user_id: str = None, playlist_names: List[str] = None):
        """Build the song database from user's playlists"""
        logger.info("🚀 Starting database build process...")
        
        # Get access token
        self.get_access_token_for_user(user_id)
        
        # Get user's playlists
        playlists = self.get_user_playlists(user_id)
        
        # Log all found playlists
        logger.info(f"📋 Found {len(playlists)} playlists:")
        for playlist in playlists:
            logger.info(f"  - {playlist.get('name', 'Unknown')} ({playlist.get('tracks', {}).get('total', 0)} tracks)")
        
        if playlist_names:
            # Filter playlists by name
            playlists = [p for p in playlists if p.get("name") in playlist_names]
            logger.info(f"📋 Filtering to {len(playlists)} specified playlists")
        
        all_tracks = []
        
        # Collect all tracks from playlists
        for playlist in playlists:
            playlist_name = playlist.get("name", "Unknown")
            playlist_id = playlist.get("id")
            
            logger.info(f"📂 Processing playlist: {playlist_name}")
            
            tracks = self.get_playlist_tracks(playlist_id)
            all_tracks.extend(tracks)
            
            logger.info(f"✅ Added {len(tracks)} tracks from {playlist_name}")
        
        # Also get liked songs
        logger.info("📂 Processing Liked Songs...")
        from utils.spotify import get_liked_songs
        liked_tracks = get_liked_songs(self.access_token)
        all_tracks.extend(liked_tracks)
        logger.info(f"✅ Added {len(liked_tracks)} liked tracks")
        
        # Remove duplicates based on Spotify ID
        unique_tracks = {}
        for track in all_tracks:
            if track.get("id"):
                unique_tracks[track["id"]] = track
        
        logger.info(f"🎵 Total unique tracks found: {len(unique_tracks)}")
        
        # Get audio features for all tracks
        track_ids = list(unique_tracks.keys())
        audio_features = self.get_audio_features(track_ids)
        
        # Save tracks to database
        for track_id, track in unique_tracks.items():
            self.save_song_to_db(track, audio_features)
        
        logger.info("🎉 Database build completed!")
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the song database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = cursor.fetchone()[0]
        
        # Get unique artists
        cursor.execute("SELECT COUNT(DISTINCT artist) FROM songs")
        unique_artists = cursor.fetchone()[0]
        
        # Get year distribution
        cursor.execute("""
            SELECT release_year, COUNT(*) 
            FROM songs 
            WHERE release_year IS NOT NULL 
            GROUP BY release_year 
            ORDER BY release_year
        """)
        year_distribution = dict(cursor.fetchall())
        
        # Get average audio features
        cursor.execute("""
            SELECT 
                AVG(valence), AVG(energy), AVG(danceability), 
                AVG(acousticness), AVG(instrumentalness), AVG(tempo)
            FROM songs
        """)
        avg_features = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_songs": total_songs,
            "unique_artists": unique_artists,
            "year_distribution": year_distribution,
            "average_features": {
                "valence": avg_features[0],
                "energy": avg_features[1],
                "danceability": avg_features[2],
                "acousticness": avg_features[3],
                "instrumentalness": avg_features[4],
                "tempo": avg_features[5]
            }
        }

def main():
    """Main function to run the database builder"""
    print("🎵 VibeAI v2 - Song Database Builder")
    print("=" * 50)
    
    # Initialize the builder
    builder = SongDatabaseBuilder()
    
    # Build database from your playlists
    # You can specify specific playlist names or leave empty for all playlists
    playlist_names = [
        # Add specific playlist names here if you want to limit to certain playlists
        # "My Favorites", "Workout Mix", etc.
    ]
    
    try:
        # Build the database using your personal account (not service account)
        # Use your personal user ID: 31r4bejefnssdwtcfgw6kf3niv4i
        print("🔍 Getting your personal playlists...")
        builder.build_database_from_playlists(user_id="31r4bejefnssdwtcfgw6kf3niv4i", playlist_names=playlist_names)
        
        # Show statistics
        stats = builder.get_database_stats()
        print("\n📊 Database Statistics:")
        print(f"Total songs: {stats['total_songs']}")
        print(f"Unique artists: {stats['unique_artists']}")
        if stats['average_features']['valence'] is not None:
            print(f"Average valence: {stats['average_features']['valence']:.3f}")
        if stats['average_features']['energy'] is not None:
            print(f"Average energy: {stats['average_features']['energy']:.3f}")
        if stats['average_features']['danceability'] is not None:
            print(f"Average danceability: {stats['average_features']['danceability']:.3f}")
        
        print("\n🎉 Database build completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database build failed: {e}")
        raise

if __name__ == "__main__":
    main() 