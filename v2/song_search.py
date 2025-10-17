#!/usr/bin/env python3
"""
VibeAI v2 - Natural Language Song Search
This script uses Gemini 2.5 Pro to convert natural language queries into structured JSON
and then searches the song database to return matching songs.
"""

import psycopg2
import json
import google.generativeai as genai
import sys
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.config import Gemini_API_KEY, DATABASE_URL
from vector_embeddings import VectorEmbeddingManager

class SongSearchEngine:
    def __init__(self, db_url: str = None):
        if db_url is None:
            self.db_url = DATABASE_URL
        else:
            self.db_url = db_url
        self.init_gemini()
        self.vector_manager = VectorEmbeddingManager(db_url)
    
    def init_gemini(self):
        """Initialize Gemini Flash with search capabilities"""
        genai.configure(api_key=Gemini_API_KEY)
        
        # Use Gemini Flash with search for better real-time information
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def parse_natural_language_query(self, user_query: str) -> Dict:
        """
        Convert natural language query into structured JSON for database search
        
        Args:
            user_query: Natural language description of what songs the user wants
            
        Returns:
            Dictionary with structured search parameters
        """
        
        prompt = f"""
        You are a music search expert. Convert the following natural language query into a structured JSON format for searching a song database.

        User Query: "{user_query}"

        The database has the following searchable fields:
        - energy_level: 0-10 (0=very low energy, 10=very high energy)
        - emotion_vector: [Happy, Sad, Angry] scores 0-10 each
        - language: Primary language (English, Hindi, Tamil, Telugu, etc.)
        - genre: Musical genre (Pop, Rock, Hip-Hop, R&B, Electronic, Country, Jazz, Classical, Folk, Indie, Bollywood, Tamil Film, etc.)
        - lyrical_themes: Array of themes like ["In Love", "Feel Good", "Motivational", "Breakup", etc.]
        - danceability_score: 0-10 (0=not danceable, 10=very danceable)
        - tempo: 0-10 (0=very slow, 10=very fast)
        - melodic_expressiveness: 0-10 (0=minimal melody, 10=highly melodic)
        - vocal_prominence: 0-10 (0=mostly instrumental, 10=vocals are main focus)
        - timbre: 0-10 (0=warm/mellow, 10=bright/punchy)
        - acousticness: 0-10 (0=electronic, 10=natural instruments)
        - popularity_score: 0-10 (1=obscure, 10=global hit)
        - artist: Artist name
        - title: Song title
        - release_year: Year of release

        Available lyrical themes:
        Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup, Friendship, Family, Feel Good, Celebrating Life, Carefree, Escape from Life, Unhappy with life, Dreaming, Motivational, Reassuring, Confident, Insecure, Love Myself, Hate Myself, Reflection/Introspection, Nostalgia, Home, Adventure, Solitude, Spirituality

        Convert the query into a JSON object with these possible fields:
        - energy_range: [min, max] or single value
        - emotion_preference: "happy", "sad", "angry", or [happy_score, sad_score, angry_score]
        - languages: ["English", "Hindi", etc.] or null for any
        - genres: ["Pop", "Rock", etc.] or null for any
        - themes: ["In Love", "Feel Good", etc.] or null for any
        - danceability_range: [min, max] or single value
        - tempo_range: [min, max] or single value
        - melodic_range: [min, max] or single value
        - vocal_range: [min, max] or single value
        - timbre_range: [min, max] or single value
        - acousticness_range: [min, max] or single value
        - popularity_range: [min, max] or single value
        - artist_contains: partial artist name or null
        - title_contains: partial song title or null
        - year_range: [min, max] or single value
        - limit: maximum number of results (default 20)

        Examples:
        - "I want happy, energetic songs" → {{"energy_range": [7, 10], "emotion_preference": "happy", "limit": 20}}
        - "Sad breakup songs in Hindi" → {{"emotion_preference": "sad", "themes": ["Breakup"], "languages": ["Hindi"], "limit": 20}}
        - "Danceable Bollywood songs" → {{"danceability_range": [7, 10], "genres": ["Bollywood"], "limit": 20}}
        - "Songs by A.R. Rahman" → {{"artist_contains": "A.R. Rahman", "limit": 20}}
        - "Slow romantic songs" → {{"tempo_range": [0, 4], "themes": ["In Love", "Hopeful Love"], "limit": 20}}

        Return ONLY the JSON object, no other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            # Parse JSON
            search_params = json.loads(text.strip())
            return search_params
            
        except Exception as e:
            print(f"❌ Error parsing query: {e}")
            return {"limit": 20}  # Return default search with just limit
    
    def search_songs(self, search_params: Dict) -> List[Dict]:
        """
        Search the song database using structured parameters
        
        Args:
            search_params: Dictionary with search criteria
            
        Returns:
            List of matching songs with their details
        """
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Build the WHERE clause dynamically
        where_conditions = []
        params = []
        
        # Energy level
        if 'energy_range' in search_params:
            energy_range = search_params['energy_range']
            if isinstance(energy_range, list):
                where_conditions.append("energy_level BETWEEN ? AND ?")
                params.extend([energy_range[0], energy_range[1]])
            else:
                where_conditions.append("energy_level >= ?")
                params.append(energy_range)
        
        # Emotion preference
        if 'emotion_preference' in search_params:
            emotion_pref = search_params['emotion_preference']
            if emotion_pref == "happy":
                where_conditions.append("CAST(SUBSTR(mood_tags, 1, INSTR(mood_tags, ',') - 1) AS INTEGER) >= 7")
            elif emotion_pref == "sad":
                where_conditions.append("CAST(SUBSTR(mood_tags, INSTR(mood_tags, ',') + 1, INSTR(SUBSTR(mood_tags, INSTR(mood_tags, ',') + 1), ',') - 1) AS INTEGER) >= 7")
            elif emotion_pref == "angry":
                where_conditions.append("CAST(SUBSTR(mood_tags, LENGTH(mood_tags) - INSTR(REVERSE(mood_tags), ',') + 2) AS INTEGER) >= 7")
        
        # Languages
        if 'languages' in search_params and search_params['languages']:
            languages = search_params['languages']
            placeholders = ','.join(['?' for _ in languages])
            where_conditions.append(f"language IN ({placeholders})")
            params.extend(languages)
        
        # Genres
        if 'genres' in search_params and search_params['genres']:
            genres = search_params['genres']
            placeholders = ','.join(['?' for _ in genres])
            where_conditions.append(f"genre IN ({placeholders})")
            params.extend(genres)
        
        # Lyrical themes
        if 'themes' in search_params and search_params['themes']:
            themes = search_params['themes']
            theme_conditions = []
            for theme in themes:
                theme_conditions.append("lyrical_themes LIKE ?")
                params.append(f"%{theme}%")
            where_conditions.append(f"({' OR '.join(theme_conditions)})")
        
        # Danceability
        if 'danceability_range' in search_params:
            dance_range = search_params['danceability_range']
            if isinstance(dance_range, list):
                where_conditions.append("danceability_score BETWEEN ? AND ?")
                params.extend([dance_range[0], dance_range[1]])
            else:
                where_conditions.append("danceability_score >= ?")
                params.append(dance_range)
        
        # Tempo
        if 'tempo_range' in search_params:
            tempo_range = search_params['tempo_range']
            if isinstance(tempo_range, list):
                where_conditions.append("tempo BETWEEN ? AND ?")
                params.extend([tempo_range[0], tempo_range[1]])
            else:
                where_conditions.append("tempo >= ?")
                params.append(tempo_range)
        
        # Melodic expressiveness
        if 'melodic_range' in search_params:
            melodic_range = search_params['melodic_range']
            if isinstance(melodic_range, list):
                where_conditions.append("melodic_expressiveness BETWEEN ? AND ?")
                params.extend([melodic_range[0], melodic_range[1]])
            else:
                where_conditions.append("melodic_expressiveness >= ?")
                params.append(melodic_range)
        
        # Vocal prominence
        if 'vocal_range' in search_params:
            vocal_range = search_params['vocal_range']
            if isinstance(vocal_range, list):
                where_conditions.append("vocal_prominence BETWEEN ? AND ?")
                params.extend([vocal_range[0], vocal_range[1]])
            else:
                where_conditions.append("vocal_prominence >= ?")
                params.append(vocal_range)
        
        # Timbre
        if 'timbre_range' in search_params:
            timbre_range = search_params['timbre_range']
            if isinstance(timbre_range, list):
                where_conditions.append("timbre BETWEEN ? AND ?")
                params.extend([timbre_range[0], timbre_range[1]])
            else:
                where_conditions.append("timbre >= ?")
                params.append(timbre_range)
        
        # Acousticness
        if 'acousticness_range' in search_params:
            acoustic_range = search_params['acousticness_range']
            if isinstance(acoustic_range, list):
                where_conditions.append("acousticness BETWEEN ? AND ?")
                params.extend([acoustic_range[0], acoustic_range[1]])
            else:
                where_conditions.append("acousticness >= ?")
                params.append(acoustic_range)
        
        # Popularity
        if 'popularity_range' in search_params:
            pop_range = search_params['popularity_range']
            if isinstance(pop_range, list):
                where_conditions.append("popularity_score BETWEEN ? AND ?")
                params.extend([pop_range[0], pop_range[1]])
            else:
                where_conditions.append("popularity_score >= ?")
                params.append(pop_range)
        
        # Artist contains
        # Artist contains - handle both single string and list
        if 'artist_contains' in search_params and search_params['artist_contains']:
            artist_value = search_params['artist_contains']
            if isinstance(artist_value, list):
                # Multiple artists - use OR logic
                artist_conditions = []
                for artist in artist_value:
                    artist_conditions.append("LOWER(artist) LIKE ?")
                    params.append(f"%{artist.lower()}%")
                where_conditions.append(f"({' OR '.join(artist_conditions)})")
            else:
                # Single artist
                where_conditions.append("LOWER(artist) LIKE ?")
                params.append(f"%{artist_value.lower()}%")        
        # Title contains
        if 'title_contains' in search_params and search_params['title_contains']:
            where_conditions.append("title LIKE ?")
            params.append(f"%{search_params['title_contains']}%")
        
        # Year range
        if 'year_range' in search_params:
            year_range = search_params['year_range']
            if isinstance(year_range, list):
                where_conditions.append("release_year BETWEEN ? AND ?")
                params.extend([year_range[0], year_range[1]])
            else:
                where_conditions.append("release_year >= ?")
                params.append(year_range)
        
        # Build the complete query
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        limit = search_params.get('limit', 20)
        
        query = f"""
            SELECT 
                id, spotify_id, title, artist, album, release_year, energy_level, 
                mood_tags, language, genre, lyrical_themes, danceability_score,
                tempo, melodic_expressiveness, vocal_prominence, timbre,
                acousticness, popularity_score, song_description
            FROM songs 
            WHERE {where_clause}
            ORDER BY popularity_score DESC, energy_level DESC
            LIMIT ?
        """
        
        params.append(limit)
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            songs = []
            for row in results:
                song = dict(row)
                # Parse lyrical themes if it's a JSON string
                if song['lyrical_themes']:
                    try:
                        song['lyrical_themes'] = json.loads(song['lyrical_themes'])
                    except:
                        song['lyrical_themes'] = song['lyrical_themes'].split(',') if song['lyrical_themes'] else []
                else:
                    song['lyrical_themes'] = []
                
                songs.append(song)
            
            return songs
            
        except Exception as e:
            print(f"❌ Database search error: {e}")
            return []
        finally:
            conn.close()
    
    def search_with_natural_language(self, user_query: str) -> List[Dict]:
        """
        Complete search pipeline: parse natural language and search database
        
        Args:
            user_query: Natural language description of desired songs
            
        Returns:
            List of matching songs
        """
        print(f"🔍 Parsing query: '{user_query}'")
        
        # Parse the natural language query
        search_params = self.parse_natural_language_query(user_query)
        print(f"📋 Search parameters: {json.dumps(search_params, indent=2)}")
        
        # Search the database
        songs = self.search_songs(search_params)
        
        return songs
    
    def search_with_vector_similarity(self, user_query: str, limit: int = 20) -> List[Dict]:
        """
        Search songs using vector similarity only
        
        Args:
            user_query: Natural language description of desired songs
            limit: Maximum number of results to return
            
        Returns:
            List of matching songs with similarity scores
        """
        print(f"🔍 Vector similarity search for: '{user_query}'")
        
        # Use vector similarity search
        similar_songs = self.vector_manager.search_similar_songs(user_query, limit)
        
        return similar_songs
    
    def search_with_hybrid_approach(self, user_query: str, limit: int = 20, vector_weight: float = 0.7) -> List[Dict]:
        """
        Hybrid search combining vector similarity and structured search
        
        Args:
            user_query: Natural language description of desired songs
            limit: Maximum number of results to return
            vector_weight: Weight for vector similarity (0.0 to 1.0)
            
        Returns:
            List of matching songs with combined scores
        """
        print(f"🔍 Hybrid search for: '{user_query}' (vector weight: {vector_weight})")
        
        # Get vector similarity results
        vector_results = self.vector_manager.search_similar_songs(user_query, limit * 2)
        
        # Get structured search results
        search_params = self.parse_natural_language_query(user_query)
        structured_results = self.search_songs(search_params)
        
        # Create a combined scoring system
        combined_results = {}
        
        # Add vector similarity scores
        for song in vector_results:
            song_id = song['id']
            combined_results[song_id] = {
                'song': song,
                'vector_score': song['similarity_score'],
                'structured_score': 0.0,
                'combined_score': 0.0
            }
        
        # Add structured search scores (normalize by popularity and energy)
        for song in structured_results:
            song_id = song['id']
            
            # Calculate structured score based on popularity and energy
            popularity_score = song.get('popularity_score', 0) / 10.0
            energy_score = song.get('energy_level', 0) / 10.0
            structured_score = (popularity_score + energy_score) / 2.0
            
            if song_id in combined_results:
                combined_results[song_id]['structured_score'] = structured_score
            else:
                combined_results[song_id] = {
                    'song': song,
                    'vector_score': 0.0,
                    'structured_score': structured_score,
                    'combined_score': 0.0
                }
        
        # Calculate combined scores
        for song_id, data in combined_results.items():
            vector_score = data['vector_score']
            structured_score = data['structured_score']
            
            # Combine scores with weighted average
            combined_score = (vector_weight * vector_score) + ((1 - vector_weight) * structured_score)
            data['combined_score'] = combined_score
        
        # Sort by combined score and return top results
        sorted_results = sorted(combined_results.values(), key=lambda x: x['combined_score'], reverse=True)
        
        # Return songs with metadata
        final_results = []
        for result in sorted_results[:limit]:
            song = result['song'].copy()
            song['vector_score'] = result['vector_score']
            song['structured_score'] = result['structured_score']
            song['combined_score'] = result['combined_score']
            final_results.append(song)
        
        print(f"📊 Found {len(final_results)} songs using hybrid approach")
        return final_results
    
    def display_results(self, songs: List[Dict], query: str):
        """Display search results in a formatted way"""
        print(f"\n🎵 Search Results for: '{query}'")
        print("=" * 60)
        
        if not songs:
            print("❌ No songs found matching your criteria.")
            return
        
        print(f"📊 Found {len(songs)} songs:\n")
        
        for i, song in enumerate(songs, 1):
            print(f"{i:2d}. {song['title']} - {song['artist']}")
            print(f"    Album: {song['album']} ({song['release_year']})")
            print(f"    Genre: {song['genre']} | Language: {song['language']}")
            print(f"    Energy: {song['energy_level']}/10 | Danceability: {song['danceability_score']}/10")
            print(f"    Popularity: {song['popularity_score']}/10")
            
            # Show scoring information if available
            if 'similarity_score' in song:
                print(f"    Vector Similarity: {song['similarity_score']:.3f}")
            if 'combined_score' in song:
                print(f"    Combined Score: {song['combined_score']:.3f} (Vector: {song.get('vector_score', 0):.3f}, Structured: {song.get('structured_score', 0):.3f})")
            
            if song['lyrical_themes']:
                themes_str = ', '.join(song['lyrical_themes'][:3])  # Show first 3 themes
                print(f"    Themes: {themes_str}")
            if song['song_description']:
                print(f"    Description: {song['song_description'][:100]}...")
            print()

def main():
    """Interactive search interface"""
    print("🎵 VibeAI v2 - Enhanced Song Search with Vector Embeddings")
    print("=" * 60)
    print("Ask me to find songs in natural language!")
    print("Examples:")
    print("- 'I want happy, energetic songs'")
    print("- 'Sad breakup songs in Hindi'")
    print("- 'Danceable Bollywood songs'")
    print("- 'Songs by A.R. Rahman'")
    print("- 'Slow romantic songs'")
    print("- 'Motivational workout songs'")
    print("\nSearch Methods:")
    print("1. Traditional structured search")
    print("2. Vector similarity search")
    print("3. Hybrid search (combines both)")
    print("\nType 'quit' to exit.\n")
    
    # Initialize search engine
    search_engine = SongSearchEngine()
    
    while True:
        try:
            # Get user input
            user_query = input("🎤 What songs are you looking for? ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_query:
                continue
            
            # Ask for search method
            print("\nChoose search method:")
            print("1. Traditional search")
            print("2. Vector similarity search")
            print("3. Hybrid search")
            
            method_choice = input("Enter choice (1-3, default=3): ").strip()
            
            if method_choice == '1':
                # Traditional structured search
                songs = search_engine.search_with_natural_language(user_query)
            elif method_choice == '2':
                # Vector similarity search
                songs = search_engine.search_with_vector_similarity(user_query)
            else:
                # Hybrid search (default)
                songs = search_engine.search_with_hybrid_approach(user_query)
            
            # Display results
            search_engine.display_results(songs, user_query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
