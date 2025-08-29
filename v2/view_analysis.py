#!/usr/bin/env python3
"""
VibeAI v2 - View Song Analysis Results
Script to explore and query analyzed songs
"""

import sqlite3
import json
from typing import List, Dict

class AnalysisViewer:
    def __init__(self, db_path: str = "song_database.db"):
        self.db_path = db_path
    
    def get_analyzed_songs(self, limit: int = 20) -> List[Dict]:
        """Get all analyzed songs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, album, mood_tags, lyrical_themes
            FROM songs
            WHERE lyrical_themes IS NOT NULL AND lyrical_themes != ''
            ORDER BY title
            LIMIT ?
        """, (limit,))
        
        songs = []
        for row in cursor.fetchall():
            title, artist, album, mood_tags, lyrical_themes = row
            
            # Parse lyrical themes JSON
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            songs.append({
                "title": title,
                "artist": artist,
                "album": album,
                "mood_tags": mood_tags,
                "energy_level": themes_data.get("energy_level", 0),
                "emotion_vector": themes_data.get("emotion_vector", [0, 0, 0]),
                "language": themes_data.get("language", "Unknown"),
                "genre": themes_data.get("genre", "Unknown"),
                "danceability_score": themes_data.get("danceability_score", 0),
                "lyrical_themes": themes_data.get("lyrical_themes", []),
                "theme_scores": themes_data.get("theme_scores", {}),
                "popularity_score": themes_data.get("popularity_score", 0)
            })
        
        conn.close()
        return songs
    
    def search_by_emotion(self, emotion_type: str, min_score: int = 5) -> List[Dict]:
        """Find songs by emotion type (happy, sad, angry) with minimum score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all songs with emotion data and filter in Python
        cursor.execute("""
            SELECT title, artist, mood_tags, lyrical_themes
            FROM songs
            WHERE lyrical_themes IS NOT NULL AND lyrical_themes != ''
            ORDER BY title
        """)
        
        songs = []
        for row in cursor.fetchall():
            title, artist, mood_tags, lyrical_themes = row
            
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            emotion_vector = themes_data.get("emotion_vector", [0, 0, 0])
            if isinstance(emotion_vector, list) and len(emotion_vector) == 3:
                emotion_index = {"happy": 0, "sad": 1, "angry": 2}.get(emotion_type.lower(), 0)
                if emotion_vector[emotion_index] >= min_score:
                    songs.append({
                        "title": title,
                        "artist": artist,
                        "mood_tags": mood_tags,
                        "energy_level": themes_data.get("energy_level", "Unknown"),
                        "emotion_vector": emotion_vector,
                        "genre": themes_data.get("genre", "Unknown"),
                        "lyrical_themes": themes_data.get("lyrical_themes", [])
                    })
        
        conn.close()
        return songs
    
    def search_by_danceability(self, min_score: int = 7) -> List[Dict]:
        """Find songs by danceability score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, mood_tags, lyrical_themes
            FROM songs
            WHERE danceability_score >= ?
            ORDER BY danceability_score DESC
        """, (min_score,))
        
        songs = []
        for row in cursor.fetchall():
            title, artist, mood_tags, lyrical_themes = row
            
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            songs.append({
                "title": title,
                "artist": artist,
                "mood_tags": mood_tags,
                "energy_level": themes_data.get("energy_level", 0),
                "emotion_vector": themes_data.get("emotion_vector", [0, 0, 0]),
                "language": themes_data.get("language", "Unknown"),
                "genre": themes_data.get("genre", "Unknown"),
                "danceability_score": themes_data.get("danceability_score", 0),
                "lyrical_themes": themes_data.get("lyrical_themes", []),
                "theme_scores": themes_data.get("theme_scores", {}),
                "popularity_score": themes_data.get("popularity_score", 0)
            })
        
        conn.close()
        return songs
    
    def search_by_energy(self, energy_level: str) -> List[Dict]:
        """Find songs by energy level"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, mood_tags, lyrical_themes
            FROM songs
            WHERE lyrical_themes LIKE ?
            ORDER BY title
        """, (f"%{energy_level}%",))
        
        songs = []
        for row in cursor.fetchall():
            title, artist, mood_tags, lyrical_themes = row
            
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            songs.append({
                "title": title,
                "artist": artist,
                "mood_tags": mood_tags,
                "energy_level": themes_data.get("energy_level", "Unknown"),
                "emotion_vector": themes_data.get("emotion_vector", "Unknown"),
                "lyrical_themes": themes_data.get("lyrical_themes", [])
            })
        
        conn.close()
        return songs
    
    def search_by_language(self, language: str) -> List[Dict]:
        """Find songs by language"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, mood_tags, lyrical_themes, language
            FROM songs
            WHERE language LIKE ?
            ORDER BY title
        """, (f"%{language}%",))
        
        songs = []
        for row in cursor.fetchall():
            title, artist, mood_tags, lyrical_themes, language = row
            
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            songs.append({
                "title": title,
                "artist": artist,
                "mood_tags": mood_tags,
                "energy_level": themes_data.get("energy_level", 0),
                "emotion_vector": themes_data.get("emotion_vector", [0, 0, 0]),
                "language": themes_data.get("language", "Unknown"),
                "genre": themes_data.get("genre", "Unknown"),
                "lyrical_themes": themes_data.get("lyrical_themes", []),
                "theme_scores": themes_data.get("theme_scores", {}),
                "popularity_score": themes_data.get("popularity_score", 0)
            })
        
        conn.close()
        return songs
    
    def search_by_genre(self, genre: str) -> List[Dict]:
        """Find songs by genre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, mood_tags, lyrical_themes
            FROM songs
            WHERE lyrical_themes LIKE ?
            ORDER BY title
        """, (f"%{genre}%",))
        
        songs = []
        for row in cursor.fetchall():
            title, artist, mood_tags, lyrical_themes = row
            
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            songs.append({
                "title": title,
                "artist": artist,
                "mood_tags": mood_tags,
                "energy_level": themes_data.get("energy_level", "Unknown"),
                "emotion_vector": themes_data.get("emotion_vector", "Unknown"),
                "genre": themes_data.get("genre", "Unknown"),
                "lyrical_themes": themes_data.get("lyrical_themes", [])
            })
        
        conn.close()
        return songs
    
    def search_by_theme(self, theme: str) -> List[Dict]:
        """Find songs by lyrical theme"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, artist, mood_tags, lyrical_themes
            FROM songs
            WHERE lyrical_themes LIKE ?
            ORDER BY title
        """, (f"%{theme}%",))
        
        songs = []
        for row in cursor.fetchall():
            title, artist, mood_tags, lyrical_themes = row
            
            themes_data = {}
            if lyrical_themes:
                try:
                    themes_data = json.loads(lyrical_themes)
                except:
                    themes_data = {}
            
            songs.append({
                "title": title,
                "artist": artist,
                "mood_tags": mood_tags,
                "energy_level": themes_data.get("energy_level", "Unknown"),
                "emotion_vector": themes_data.get("emotion_vector", "Unknown"),
                "lyrical_themes": themes_data.get("lyrical_themes", [])
            })
        
        conn.close()
        return songs
    
    def get_analysis_stats(self) -> Dict:
        """Get statistics about analyzed songs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total analyzed songs
        cursor.execute("SELECT COUNT(*) FROM songs WHERE lyrical_themes IS NOT NULL AND lyrical_themes != ''")
        total_analyzed = cursor.fetchone()[0]
        
        # Emotion distribution
        cursor.execute("""
            SELECT mood_tags, COUNT(*) as count
            FROM songs
            WHERE mood_tags IS NOT NULL AND mood_tags != ''
            GROUP BY mood_tags
            ORDER BY count DESC
        """)
        emotion_distribution = dict(cursor.fetchall())
        
        # Energy level distribution
        cursor.execute("""
            SELECT COUNT(*) FROM songs 
            WHERE lyrical_themes LIKE '%"energy_level": "High"%'
        """)
        high_energy = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM songs 
            WHERE lyrical_themes LIKE '%"energy_level": "Medium"%'
        """)
        medium_energy = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM songs 
            WHERE lyrical_themes LIKE '%"energy_level": "Low"%'
        """)
        low_energy = cursor.fetchone()[0]
        
        # Popular themes
        cursor.execute("""
            SELECT COUNT(*) FROM songs 
            WHERE lyrical_themes LIKE '%In Love%'
        """)
        love_songs = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM songs 
            WHERE lyrical_themes LIKE '%Feel Good%'
        """)
        feel_good_songs = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM songs 
            WHERE lyrical_themes LIKE '%Dance%'
        """)
        dance_songs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_analyzed": total_analyzed,
            "emotion_distribution": emotion_distribution,
            "energy_distribution": {
                "high": high_energy,
                "medium": medium_energy,
                "low": low_energy
            },
            "popular_themes": {
                "in_love": love_songs,
                "feel_good": feel_good_songs,
                "dance": dance_songs
            }
        }

def main():
    """Main function to explore analyzed songs"""
    print("🔍 VibeAI v2 - Song Analysis Viewer")
    print("=" * 50)
    
    viewer = AnalysisViewer()
    
    # Get stats
    stats = viewer.get_analysis_stats()
    
    if stats["total_analyzed"] == 0:
        print("❌ No songs have been analyzed yet!")
        print("Run the batch analysis script first to analyze songs with ChatGPT.")
        return
    
    print(f"\n📊 Analysis Overview:")
    print(f"Total analyzed songs: {stats['total_analyzed']}")
    
    if stats["emotion_distribution"]:
        print(f"\n😊 Emotion Distribution:")
        for emotion, count in list(stats["emotion_distribution"].items())[:5]:
            print(f"  - {emotion}: {count} songs")
    
    if any(stats["energy_distribution"].values()):
        print(f"\n⚡ Energy Distribution:")
        for level, count in stats["energy_distribution"].items():
            if count > 0:
                print(f"  - {level.title()}: {count} songs")
    
    if any(stats["popular_themes"].values()):
        print(f"\n🎵 Popular Themes:")
        for theme, count in stats["popular_themes"].items():
            if count > 0:
                theme_name = theme.replace("_", "/").title()
                print(f"  - {theme_name}: {count} songs")
    
    # Show some sample analyzed songs
    print(f"\n🎵 Sample Analyzed Songs:")
    analyzed_songs = viewer.get_analyzed_songs(10)
    
    for song in analyzed_songs:
        print(f"\n  📻 {song['title']} by {song['artist']}")
        print(f"     Energy: {song['energy_level']}/10")
        emotion_vec = song['emotion_vector']
        if isinstance(emotion_vec, list) and len(emotion_vec) == 3:
            print(f"     Emotion: [Happy: {emotion_vec[0]}, Sad: {emotion_vec[1]}, Angry: {emotion_vec[2]}]")
        else:
            print(f"     Emotion: {emotion_vec}")
        print(f"     Language: {song['language']}")
        print(f"     Genre: {song['genre']}")
        print(f"     Danceability: {song['danceability_score']}/10")
        print(f"     Popularity: {song['popularity_score']}/10")
        if song['lyrical_themes']:
            themes_str = ", ".join(song['lyrical_themes'][:3])
            if len(song['lyrical_themes']) > 3:
                themes_str += f" (+{len(song['lyrical_themes']) - 3} more)"
            print(f"     Themes: {themes_str}")
            if song['theme_scores']:
                scores_str = ", ".join([f"{theme}: {score}/10" for theme, score in list(song['theme_scores'].items())[:3]])
                print(f"     Theme Scores: {scores_str}")
    
    # Interactive search
    print(f"\n" + "="*50)
    print("Search Options:")
    print("1. Search by emotion (e.g., Happy, Sad, Calm)")
    print("2. Search by energy level (High, Medium, Low)")
    print("3. Search by language (e.g., English, Tamil, Hindi)")
    print("4. Search by genre (e.g., Pop, Rock, Bollywood)")
    print("5. Search by danceability (e.g., High danceable songs)")
    print("6. Search by theme (e.g., In Love, Feel Good, Dance)")
    print("7. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            emotion = input("Enter emotion type (happy/sad/angry): ").strip().lower()
            if emotion in ["happy", "sad", "angry"]:
                min_score = input("Enter minimum score (0-10, default 5): ").strip()
                min_score = int(min_score) if min_score.isdigit() else 5
                results = viewer.search_by_emotion(emotion, min_score)
                print(f"\n🎵 Found {len(results)} songs with {emotion} score >= {min_score}:")
                for song in results[:10]:
                    emotion_vec = song['emotion_vector']
                    if isinstance(emotion_vec, list) and len(emotion_vec) == 3:
                        print(f"  - {song['title']} by {song['artist']} ([H:{emotion_vec[0]}, S:{emotion_vec[1]}, A:{emotion_vec[2]}])")
                    else:
                        print(f"  - {song['title']} by {song['artist']} ({emotion_vec})")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more")
            else:
                print("❌ Please enter 'happy', 'sad', or 'angry'")
        
        elif choice == "2":
            energy = input("Enter energy level (High/Medium/Low): ").strip()
            if energy:
                results = viewer.search_by_energy(energy)
                print(f"\n⚡ Found {len(results)} songs with {energy} energy:")
                for song in results[:10]:
                    print(f"  - {song['title']} by {song['artist']} ({song['energy_level']})")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more")
        
        elif choice == "3":
            language = input("Enter language to search for: ").strip()
            if language:
                results = viewer.search_by_language(language)
                print(f"\n🎵 Found {len(results)} songs in '{language}':")
                for song in results[:10]:
                    print(f"  - {song['title']} by {song['artist']} ({song['language']})")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more")
        
        elif choice == "4":
            genre = input("Enter genre to search for: ").strip()
            if genre:
                results = viewer.search_by_genre(genre)
                print(f"\n🎵 Found {len(results)} songs with genre '{genre}':")
                for song in results[:10]:
                    print(f"  - {song['title']} by {song['artist']} ({song['genre']})")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more")
        
        elif choice == "5":
            min_score = input("Enter minimum danceability score (0-10, default 7): ").strip()
            min_score = int(min_score) if min_score.isdigit() else 7
            results = viewer.search_by_danceability(min_score)
            print(f"\n💃 Found {len(results)} songs with danceability >= {min_score}:")
            for song in results[:10]:
                print(f"  - {song['title']} by {song['artist']} (Danceability: {song['danceability_score']}/10)")
            if len(results) > 10:
                print(f"  ... and {len(results) - 10} more")
        
        elif choice == "6":
            theme = input("Enter theme to search for: ").strip()
            if theme:
                results = viewer.search_by_theme(theme)
                print(f"\n🎵 Found {len(results)} songs with theme '{theme}':")
                for song in results[:10]:
                    themes_str = ", ".join(song['lyrical_themes'][:2])
                    print(f"  - {song['title']} by {song['artist']} ({themes_str})")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()
