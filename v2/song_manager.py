#!/usr/bin/env python3
"""
VibeAI v2 - Song Manager
Clean, modular functions for song analysis, playlist management, and database operations.
"""

import sqlite3
import json
import time
import google.generativeai as genai
import sys
import os
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Gemini_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, VibeAI_userid
from utils.token import get_access_token
from utils.spotify import get_liked_songs
from utils.groq import call_groq_api

class SongManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use absolute path to ensure we get the right database
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(os.path.dirname(current_dir), "song_database.db")
        else:
            self.db_path = db_path
        self.init_database()
        self.init_gemini()
    
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
                genre TEXT DEFAULT 'Unknown'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_gemini(self):
        """Initialize Gemini API with search capabilities"""
        genai.configure(api_key=Gemini_API_KEY)
        # Use Gemini Flash with search for better real-time information
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def get_db_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    def analyze_song_with_gemini(self, title: str, artist: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Analyze a single song using Gemini API
        
        Args:
            title: Song title
            artist: Artist name
            
        Returns:
            Tuple of (analysis_data, error_message)
        """
        
        prompt = f"""
        Analyze the following song and return the requested attributes as valid JSON. Use reliable online sources, lyrics, translations, and community interpretations to ensure accuracy.

        Song Information:
        - Title: "{title}"
        - Artist: "{artist}"
        
        Please provide:

        1. **Energy Level**: 0–10 (0=very low energy, 10=very high energy)  
        2. **Emotion Vector**: Provide a numerical vector [Happy, Sad, Angry] where each value is 0-10 (10 being strongest)
        3. **Language**: Primary language of the song (English, Tamil, Hindi, etc.)
        4. **Genre**: Primary musical genre (Pop, Rock, Hip-Hop, R&B, Electronic, Country, Jazz, Classical, Folk, Indie, Bollywood, Tamil Film, etc.)  
        5. **Lyrical Themes**: Select 1-5 most relevant themes from: Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup, Friendship, Family, Feel Good, Celebrating Life, Carefree, Escape from Life, Unhappy with life, Dreaming, Motivational, Reassuring, Confident, Insecure, Love Myself, Hate Myself, Reflection/Introspection, Nostalgia, Home, Adventure, Solitude, Spirituality
        6. **Danceability Score**: 0–10 (0 = not danceable, 10 = very danceable)  
        7. **Tempo**: 0–10 (0 = very slow/ballad, 5 = moderate, 10 = very fast/upbeat)  
        8. **Melodic Expressiveness**: 0–10 (0 = minimal melody, 10 = highly melodic)  
        9. **Vocal Prominence**: 0–10 (0 = mostly instrumental, 10 = vocals are the main focus)  
        10. **Timbre**: 0–10 (0 = warm, mellow, soft, 10 = bright, punchy, energetic)  
        11. **Acousticness**: 0–10 (0 = mostly electronic, 10 = primarily natural instruments)
        12. **Theme Scores**: For each selected lyrical theme, rate 1–10 (10 = perfectly central to the song)  
        13. **Popularity Score**: 0–10 (1 = obscure, 10 = global hit/very famous)  
        14. **Song Description**: 1–2 line summary including music style, lyrics, and overall feel  
        
        Return your response as valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            json_response = json.loads(text.strip())
            return json_response, None
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed for {title} by {artist}: {e}")
            print(f"Response text: {response.text[:200]}...")
            return None, f"JSON parsing failed: {e}"
        except Exception as e:
            print(f"❌ Gemini API error for {title} by {artist}: {e}")
            return None, f"Gemini API error: {e}"
    
    def save_song_analysis(self, song_id: int, analysis_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Save song analysis to database
        
        Args:
            song_id: Database ID of the song
            analysis_data: Analysis results from Gemini
            
        Returns:
            Tuple of (success, error_message)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract data from analysis (handle both underscore and space formats)
            energy_level = analysis_data.get('energy_level') or analysis_data.get('Energy Level', 0)
            emotion_vector = analysis_data.get('emotion_vector') or analysis_data.get('Emotion Vector', [0, 0, 0])
            language = analysis_data.get('language') or analysis_data.get('Language', 'Unknown')
            genre = analysis_data.get('genre') or analysis_data.get('Genre', 'Unknown')
            lyrical_themes = analysis_data.get('lyrical_themes') or analysis_data.get('Lyrical Themes', [])
            danceability_score = analysis_data.get('danceability_score') or analysis_data.get('Danceability Score', 0)
            tempo = analysis_data.get('tempo') or analysis_data.get('Tempo', 0)
            melodic_expressiveness = analysis_data.get('melodic_expressiveness') or analysis_data.get('Melodic Expressiveness', 0)
            vocal_prominence = analysis_data.get('vocal_prominence') or analysis_data.get('Vocal Prominence', 0)
            timbre = analysis_data.get('timbre') or analysis_data.get('Timbre', 0)
            acousticness = analysis_data.get('acousticness') or analysis_data.get('Acousticness', 0)
            theme_scores = analysis_data.get('theme_scores') or analysis_data.get('Theme Scores', {})
            popularity_score = analysis_data.get('popularity_score') or analysis_data.get('Popularity Score', 0)
            song_description = analysis_data.get('song_description') or analysis_data.get('Song Description', '')
            
            # Convert emotion vector to string format (handle both list and dict formats)
            if isinstance(emotion_vector, dict):
                # Handle format like {"Happy": 1, "Sad": 4, "Angry": 0}
                emotion_vector = [
                    emotion_vector.get('Happy', 0),
                    emotion_vector.get('Sad', 0), 
                    emotion_vector.get('Angry', 0)
                ]
            elif not isinstance(emotion_vector, list) or len(emotion_vector) < 3:
                emotion_vector = [0, 0, 0]
            emotion_str = f"{emotion_vector[0]},{emotion_vector[1]},{emotion_vector[2]}"
            
            # Convert lyrical themes to string
            themes_str = ','.join(lyrical_themes) if lyrical_themes else ''
            
            # Convert theme scores to string
            theme_scores_str = json.dumps(theme_scores) if theme_scores else '{}'
            
            # Update the song
            cursor.execute("""
                UPDATE songs SET 
                    energy_level = ?, mood_tags = ?, language = ?, genre = ?,
                    lyrical_themes = ?, danceability_score = ?, tempo = ?,
                    melodic_expressiveness = ?, vocal_prominence = ?, timbre = ?,
                    acousticness = ?, theme_scores = ?, popularity_score = ?,
                    song_description = ?, last_analyzed = ?
                WHERE id = ?
            """, (
                energy_level, emotion_str, language, genre, themes_str,
                danceability_score, tempo, melodic_expressiveness, vocal_prominence,
                timbre, acousticness, theme_scores_str, popularity_score,
                song_description, datetime.now().isoformat(), song_id
            ))
            
            conn.commit()
            return True, None
            
        except Exception as e:
            return False, f"Database update error: {e}"
        finally:
            conn.close()
    
    def analyze_playlist_songs(self, playlist_name: str = None, limit: int = 50) -> Dict:
        """
        Analyze songs from a specific playlist or all unanalyzed songs
        
        Args:
            playlist_name: Name of playlist to analyze (None for all unanalyzed)
            limit: Maximum number of songs to analyze
            
        Returns:
            Dictionary with analysis results
        """
        print(f"🔄 Starting playlist analysis...")
        print("=" * 60)
        
        # Get songs to analyze
        if playlist_name:
            songs = self.get_playlist_songs(playlist_name, limit)
        else:
            songs = self.get_unanalyzed_songs(limit)
        
        if not songs:
            print("✅ No songs found to analyze!")
            return {"analyzed": 0, "errors": 0, "total": 0}
        
        print(f"📊 Found {len(songs)} songs to analyze")
        print(f"⏱️  Rate limit: 10 requests/minute (6 second delay)")
        print(f"⏰ Estimated time: ~{len(songs) * 6 / 60:.1f} minutes")
        print("=" * 60)
        
        analyzed_count = 0
        error_count = 0
        start_time = time.time()
        
        for i, song in enumerate(songs, 1):
            print(f"\n[{i}/{len(songs)}] Analyzing: {song['title']} by {song['artist']}")
            
            # Analyze the song
            analysis_data, error = self.analyze_song_with_gemini(song['title'], song['artist'])
            
            if analysis_data:
                # Save to database
                success, db_error = self.save_song_analysis(song['id'], analysis_data)
                
                if success:
                    print(f"   ✅ Successfully analyzed and stored")
                    analyzed_count += 1
                else:
                    print(f"   ❌ Database error: {db_error}")
                    error_count += 1
            else:
                print(f"   ❌ Analysis failed: {error}")
                error_count += 1
            
            # Rate limiting
            if i < len(songs):
                print(f"   ⏳ Waiting 6 seconds for rate limit...")
                time.sleep(6)
        
        # Final summary
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📊 Total songs processed: {len(songs)}")
        print(f"✅ Successfully analyzed: {analyzed_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        
        return {
            "analyzed": analyzed_count,
            "errors": error_count,
            "total": len(songs)
        }
    
    def get_unanalyzed_songs(self, limit: int = 50) -> List[Dict]:
        """Get songs that need analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, artist, album, release_year
            FROM songs 
            WHERE energy_level = 0 OR energy_level IS NULL
            ORDER BY title
            LIMIT ?
        """, (limit,))
        
        songs = []
        for row in cursor.fetchall():
            songs.append({
                "id": row[0],
                "title": row[1],
                "artist": row[2],
                "album": row[3],
                "release_year": row[4]
            })
        
        conn.close()
        return songs
    
    def get_playlist_songs(self, playlist_name: str, limit: int = 50) -> List[Dict]:
        """Get songs from a specific playlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # This would need to be implemented based on how playlists are stored
        # For now, return unanalyzed songs
        return self.get_unanalyzed_songs(limit)
    
    def import_playlist_from_spotify(self, user_id: str = None, playlist_names: List[str] = None) -> Dict:
        """
        Import songs from Spotify playlists and check for duplicates
        
        Args:
            user_id: Spotify user ID (None for current user)
            playlist_names: List of playlist names to import (None for all)
            
        Returns:
            Dictionary with import results
        """
        print("🎵 Importing playlists from Spotify...")
        print("=" * 60)
        
        try:
            # Get access token
            access_token = get_access_token(user_id or VibeAI_userid)
            
            # Get user's playlists
            playlists = self.get_user_playlists(access_token)
            
            if playlist_names:
                playlists = [p for p in playlists if p.get("name") in playlist_names]
            
            print(f"📋 Found {len(playlists)} playlists to import")
            
            all_tracks = []
            
            # Collect tracks from playlists
            for playlist in playlists:
                playlist_name = playlist.get("name", "Unknown")
                tracks = self.get_playlist_tracks(access_token, playlist.get("id"))
                all_tracks.extend(tracks)
                print(f"✅ Added {len(tracks)} tracks from {playlist_name}")
            
            # Also get liked songs
            liked_tracks = get_liked_songs(access_token)
            all_tracks.extend(liked_tracks)
            print(f"✅ Added {len(liked_tracks)} liked tracks")
            
            # Remove duplicates and save to database
            unique_tracks = {}
            for track in all_tracks:
                if track.get("id"):
                    unique_tracks[track["id"]] = track
            
            print(f"🎵 Total unique tracks: {len(unique_tracks)}")
            
            # Get audio features and save
            track_ids = list(unique_tracks.keys())
            audio_features = self.get_audio_features(access_token, track_ids)
            
            saved_count = 0
            duplicate_count = 0
            
            for track_id, track in unique_tracks.items():
                if self.save_song_to_db(track, audio_features.get(track_id, {})):
                    saved_count += 1
                else:
                    duplicate_count += 1
            
            print(f"✅ Saved {saved_count} new songs")
            print(f"⚠️  Skipped {duplicate_count} duplicates")
            
            return {
                "total_found": len(all_tracks),
                "unique_tracks": len(unique_tracks),
                "saved": saved_count,
                "duplicates": duplicate_count
            }
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return {"error": str(e)}
    
    def get_user_playlists(self, access_token: str) -> List[Dict]:
        """Get user's playlists from Spotify"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get current user's ID
        me_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            current_user_id = user_data["id"]
        else:
            current_user_id = VibeAI_userid
        
        url = f"https://api.spotify.com/v1/users/{current_user_id}/playlists"
        
        playlists = []
        offset = 0
        limit = 50
        
        while True:
            params = {"limit": limit, "offset": offset}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            playlists.extend(data.get("items", []))
            
            if len(data.get("items", [])) < limit:
                break
            
            offset += limit
        
        return playlists
    
    def get_playlist_tracks(self, access_token: str, playlist_id: str) -> List[Dict]:
        """Get tracks from a specific playlist"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        
        tracks = []
        offset = 0
        limit = 100
        
        while True:
            params = {"limit": limit, "offset": offset}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            playlist_tracks = data.get("items", [])
            
            for item in playlist_tracks:
                if item.get("track") and item["track"].get("id"):
                    tracks.append(item["track"])
            
            if len(playlist_tracks) < limit:
                break
            
            offset += limit
        
        return tracks
    
    def get_audio_features(self, access_token: str, track_ids: List[str]) -> Dict[str, Dict]:
        """Get audio features for multiple tracks"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://api.spotify.com/v1/audio-features"
        
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
        
        return features
    
    def save_song_to_db(self, track: Dict, audio_features: Dict = None) -> bool:
        """Save a song to the database, return True if new, False if duplicate"""
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
            features = audio_features or {}
            
            # Check if song already exists
            cursor.execute("SELECT id FROM songs WHERE spotify_id = ?", (spotify_id,))
            if cursor.fetchone():
                return False  # Duplicate
            
            # Insert new song
            cursor.execute('''
                INSERT INTO songs (
                    spotify_id, title, artist, album, release_year, duration_ms, popularity,
                    valence, energy, danceability, acousticness, instrumentalness,
                    liveness, loudness, speechiness, tempo, key, mode, time_signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                spotify_id, title, artist, album, release_year, duration_ms, popularity,
                features.get("valence"), features.get("energy"), features.get("danceability"),
                features.get("acousticness"), features.get("instrumentalness"),
                features.get("liveness"), features.get("loudness"), features.get("speechiness"),
                features.get("tempo"), features.get("key"), features.get("mode"),
                features.get("time_signature")
            ))
            
            conn.commit()
            return True  # New song saved
            
        except Exception as e:
            print(f"❌ Failed to save song {title}: {e}")
            return False
        finally:
            conn.close()
    
    def find_duplicates(self) -> List[Dict]:
        """Find duplicate songs in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, COUNT(*) as count
            FROM songs
            GROUP BY LOWER(title), LOWER(artist)
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = []
        for row in cursor.fetchall():
            duplicates.append({
                "title": row[0],
                "artist": row[1],
                "count": row[2]
            })
        
        conn.close()
        return duplicates
    
    def remove_duplicates(self, keep_analyzed: bool = True) -> int:
        """
        Remove duplicate songs from database
        
        Args:
            keep_analyzed: If True, keep songs that have been analyzed
            
        Returns:
            Number of duplicates removed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find duplicates
        if keep_analyzed:
            # Keep the analyzed version if available
            cursor.execute("""
                DELETE FROM songs 
                WHERE id NOT IN (
                    SELECT MIN(CASE 
                        WHEN energy_level > 0 THEN id 
                        ELSE MIN(id) 
                    END)
                    FROM songs
                    GROUP BY LOWER(title), LOWER(artist)
                )
            """)
        else:
            # Keep the first occurrence
            cursor.execute("""
                DELETE FROM songs 
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM songs
                    GROUP BY LOWER(title), LOWER(artist)
                )
            """)
        
        removed_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return removed_count
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the song database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total songs
        cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = cursor.fetchone()[0]
        
        # Analyzed songs
        cursor.execute("SELECT COUNT(*) FROM songs WHERE energy_level > 0")
        analyzed_songs = cursor.fetchone()[0]
        
        # Unique artists
        cursor.execute("SELECT COUNT(DISTINCT artist) FROM songs")
        unique_artists = cursor.fetchone()[0]
        
        # Duplicates
        duplicates = self.find_duplicates()
        duplicate_count = sum(dup['count'] - 1 for dup in duplicates)
        
        conn.close()
        
        return {
            "total_songs": total_songs,
            "analyzed_songs": analyzed_songs,
            "unanalyzed_songs": total_songs - analyzed_songs,
            "unique_artists": unique_artists,
            "duplicates": duplicate_count,
            "duplicate_groups": len(duplicates)
        }
    
    def get_playlist_from_url(self, playlist_url: str) -> Dict:
        """
        Get songs from any Spotify playlist by URL
        
        Args:
            playlist_url: Spotify playlist URL or ID
            
        Returns:
            Dictionary with import results
        """
        print("🎵 Importing playlist from Spotify URL...")
        print("=" * 60)
        
        try:
            # Extract playlist ID from URL
            playlist_id = self._extract_playlist_id(playlist_url)
            if not playlist_id:
                return {"error": "Invalid Spotify playlist URL"}
            
            # Get access token
            access_token = get_access_token(VibeAI_userid)
            
            # Get playlist tracks
            tracks = self.get_playlist_tracks(access_token, playlist_id)
            
            if not tracks:
                return {"error": "No tracks found in playlist or playlist is private"}
            
            print(f"📊 Found {len(tracks)} tracks in playlist")
            
            # Get audio features
            track_ids = [track['id'] for track in tracks if track.get('id')]
            audio_features = self.get_audio_features(access_token, track_ids)
            
            # Save tracks to database
            saved_count = 0
            duplicate_count = 0
            
            for track in tracks:
                if self.save_song_to_db(track, audio_features.get(track['id'], {})):
                    saved_count += 1
                else:
                    duplicate_count += 1
            
            print(f"✅ Saved {saved_count} new songs")
            print(f"⚠️  Skipped {duplicate_count} duplicates")
            
            return {
                "total_found": len(tracks),
                "saved": saved_count,
                "duplicates": duplicate_count,
                "playlist_id": playlist_id
            }
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return {"error": str(e)}
    
    def _extract_playlist_id(self, url_or_id: str) -> str:
        """Extract playlist ID from Spotify URL or return as-is if already an ID"""
        if not url_or_id:
            return None
        
        # If it's already a playlist ID (22 characters)
        if len(url_or_id) == 22 and url_or_id.isalnum():
            return url_or_id
        
        # Extract from URL
        if 'spotify.com/playlist/' in url_or_id:
            # Extract ID from URL like: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
            parts = url_or_id.split('/playlist/')
            if len(parts) > 1:
                playlist_id = parts[1].split('?')[0]  # Remove query parameters
                return playlist_id
        
        return None

def main():
    """Example usage of SongManager"""
    print("🎵 VibeAI v2 - Song Manager")
    print("=" * 50)
    
    # Initialize manager
    manager = SongManager()
    
    # Show current stats
    stats = manager.get_database_stats()
    print(f"📊 Database Stats:")
    print(f"   Total songs: {stats['total_songs']}")
    print(f"   Analyzed: {stats['analyzed_songs']}")
    print(f"   Unanalyzed: {stats['unanalyzed_songs']}")
    print(f"   Unique artists: {stats['unique_artists']}")
    print(f"   Duplicates: {stats['duplicates']}")
    
    # Example: Analyze 10 unanalyzed songs
    print(f"\n🔄 Analyzing 10 unanalyzed songs...")
    results = manager.analyze_playlist_songs(limit=10)
    print(f"✅ Analysis complete: {results['analyzed']} analyzed, {results['errors']} errors")

if __name__ == "__main__":
    main()

