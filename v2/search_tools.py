#!/usr/bin/env python3
"""
VibeAI v2 - Search Tools for Agentic System
This module provides tool functions that agents can use to search the song database.
"""

import psycopg2
import psycopg2.extras
import json
import sys
import os
from typing import List, Dict, Optional
from difflib import SequenceMatcher

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_embeddings import VectorEmbeddingManager
from song_search import SongSearchEngine
from utils.config import DATABASE_URL

class SearchTools:
    def __init__(self, db_url: str = None):
        if db_url is None:
            self.db_url = DATABASE_URL
        else:
            self.db_url = db_url
        
        self.vector_manager = VectorEmbeddingManager(db_url)
        self.search_engine = SongSearchEngine(db_url)
    
    def embedding_song_search(self, query_text: str, n: int = 20) -> List[Dict]:
        """
        Search songs using vector embeddings based on natural language query.
        
        Args:
            query_text: Natural language description of desired songs
            n: Maximum number of songs to return
            
        Returns:
            List of songs with match scores (0-100 percentage)
        """
        try:
            # Generate embedding for query
            query_embedding = self.vector_manager.generate_embedding(query_text)
            if not query_embedding:
                return []
            
            # Get all songs with embeddings
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT id, title, artist, album, release_year, energy_level, 
                       mood_tags, language, genre, lyrical_themes, danceability_score,
                       tempo, melodic_expressiveness, vocal_prominence, timbre,
                       acousticness, popularity_score, song_description, vector_embedding, spotify_id
                FROM songs 
                WHERE vector_embedding IS NOT NULL AND vector_embedding != ''
            """)
            
            songs_with_similarities = []
            
            for row in cursor.fetchall():
                song = dict(row)
                song_embedding_json = song.pop('vector_embedding')
                
                try:
                    song_embedding = json.loads(song_embedding_json)
                    
                    # Calculate cosine similarity
                    from sklearn.metrics.pairwise import cosine_similarity
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [song_embedding]
                    )[0][0]
                    
                    # Convert to percentage (0-100)
                    match_score = float(similarity) * 100
                    
                    song['match_score'] = match_score
                    song['spotify_uri'] = f"spotify:track:{song['spotify_id']}"
                    songs_with_similarities.append(song)
                    
                except Exception as e:
                    print(f"Error processing embedding for song {song['id']}: {e}")
                    continue
            
            conn.close()
            
            # Sort by similarity score (highest first) and return top n
            songs_with_similarities.sort(key=lambda x: x['match_score'], reverse=True)
            return songs_with_similarities[:n]
            
        except Exception as e:
            print(f"Error in embedding search: {e}")
            return []
    
    def song_filter_search(self, filters: Dict, limit: int = 20) -> List[Dict]:
        """
        Search songs using structured filters.
        
        Args:
            filters: Dictionary with filter criteria
            limit: Maximum number of songs to return
            
        Returns:
            List of songs matching the filters
        """
        try:
            # Use existing search engine
            songs = self.search_engine.search_songs(filters)
            
            # Add spotify_uri and match_score to each song
            for song in songs:
                spotify_id = song.get('spotify_id')
                if spotify_id and spotify_id.strip():  # Only create URI if spotify_id exists and is not empty
                    song['spotify_uri'] = f"spotify:track:{spotify_id}"
                else:
                    song['spotify_uri'] = None  # Explicitly set to None if no valid spotify_id
                
                # Calculate a basic match score based on popularity and energy
                popularity_score = song.get('popularity_score', 0) / 10.0
                energy_score = song.get('energy_level', 0) / 10.0
                song['match_score'] = (popularity_score + energy_score) * 50  # Scale to 0-100
            
            return songs[:limit]
            
        except Exception as e:
            print(f"Error in filter search: {e}")
            return []
    
    def search_songs_by_name(self, song_list: List[Dict]) -> List[Dict]:
        """
        Search for songs by exact or fuzzy matching of title and artist.
        
        Args:
            song_list: List of dictionaries with 'title' and 'artist' keys
            
        Returns:
            List of matching songs with spotify_uri
        """
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            results = []
            
            for song_info in song_list:
                title = song_info.get('title', '').strip()
                artist = song_info.get('artist', '').strip()
                
                if not title and not artist:
                    continue
                
                # Try exact match first
                if title and artist:
                    cursor.execute("""
                        SELECT id, title, artist, album, release_year, spotify_id,
                               energy_level, popularity_score, genre, language
                        FROM songs 
                        WHERE LOWER(title) = LOWER(?) AND LOWER(artist) = LOWER(?)
                    """, (title, artist))
                elif title:
                    cursor.execute("""
                        SELECT id, title, artist, album, release_year, spotify_id,
                               energy_level, popularity_score, genre, language
                        FROM songs 
                        WHERE LOWER(title) = LOWER(?)
                    """, (title,))
                elif artist:
                    cursor.execute("""
                        SELECT id, title, artist, album, release_year, spotify_id,
                               energy_level, popularity_score, genre, language
                        FROM songs 
                        WHERE LOWER(artist) = LOWER(?)
                    """, (artist,))
                
                exact_match = cursor.fetchone()
                if exact_match:
                    song = dict(exact_match)
                    song['spotify_uri'] = f"spotify:track:{song['spotify_id']}"
                    song['match_score'] = 100.0  # Perfect match
                    results.append(song)
                    continue
                
                # Try fuzzy matching if no exact match
                cursor.execute("""
                    SELECT id, title, artist, album, release_year, spotify_id,
                           energy_level, popularity_score, genre, language
                    FROM songs
                """)
                
                all_songs = cursor.fetchall()
                best_match = None
                best_score = 0.0
                
                for row in all_songs:
                    song_title = row['title'].lower()
                    song_artist = row['artist'].lower()
                    
                    # Calculate similarity scores
                    title_sim = SequenceMatcher(None, title.lower(), song_title).ratio()
                    artist_sim = SequenceMatcher(None, artist.lower(), song_artist).ratio()
                    
                    # Combined score (weighted average)
                    if title and artist:
                        combined_score = (title_sim * 0.7) + (artist_sim * 0.3)
                    elif title:
                        combined_score = title_sim
                    else:
                        combined_score = artist_sim
                    
                    if combined_score > best_score and combined_score > 0.6:  # Threshold for fuzzy match
                        best_score = combined_score
                        best_match = row
                
                if best_match:
                    song = dict(best_match)
                    song['spotify_uri'] = f"spotify:track:{song['spotify_id']}"
                    song['match_score'] = best_score * 100  # Convert to percentage
                    results.append(song)
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error in name search: {e}")
            return []
    
    def get_song_embedding(self, spotify_id: str) -> Optional[List[float]]:
        """
        Retrieve vector embedding for a specific song by Spotify ID.
        
        Args:
            spotify_id: Spotify track ID
            
        Returns:
            List of float values representing the embedding, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT vector_embedding FROM songs WHERE spotify_id = ?", (spotify_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            print(f"Error retrieving embedding for {spotify_id}: {e}")
            return None
        finally:
            conn.close()
    
    def generate_query_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate vector embedding for natural language text.
        
        Args:
            text: Natural language query
            
        Returns:
            List of float values representing the embedding, or None if failed
        """
        return self.vector_manager.generate_embedding(text)
    
    def search_songs_like(self, reference_song: Dict, n: int = 20) -> List[Dict]:
        """
        Find songs similar to a reference song using vector embeddings.
        
        Args:
            reference_song: Dictionary with 'title' and 'artist' keys
            n: Maximum number of similar songs to return
            
        Returns:
            List of similar songs with match scores
        """
        try:
            # First, find the reference song in our database
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT spotify_id, vector_embedding FROM songs 
                WHERE LOWER(title) = LOWER(?) AND LOWER(artist) = LOWER(?)
            """, (reference_song['title'], reference_song['artist']))
            
            ref_song = cursor.fetchone()
            if not ref_song or not ref_song['vector_embedding']:
                conn.close()
                return []
            
            ref_embedding = json.loads(ref_song['vector_embedding'])
            ref_spotify_id = ref_song['spotify_id']
            
            # Get all songs with embeddings
            cursor.execute("""
                SELECT id, title, artist, album, release_year, energy_level, 
                       mood_tags, language, genre, lyrical_themes, danceability_score,
                       tempo, melodic_expressiveness, vocal_prominence, timbre,
                       acousticness, popularity_score, song_description, vector_embedding, spotify_id
                FROM songs 
                WHERE vector_embedding IS NOT NULL AND vector_embedding != '' 
                AND spotify_id != ?
            """, (ref_spotify_id,))
            
            similar_songs = []
            
            for row in cursor.fetchall():
                song = dict(row)
                song_embedding_json = song.pop('vector_embedding')
                
                try:
                    song_embedding = json.loads(song_embedding_json)
                    
                    # Calculate cosine similarity
                    from sklearn.metrics.pairwise import cosine_similarity
                    similarity = cosine_similarity(
                        [ref_embedding], 
                        [song_embedding]
                    )[0][0]
                    
                    # Convert to percentage (0-100)
                    match_score = float(similarity) * 100
                    
                    song['match_score'] = match_score
                    song['spotify_uri'] = f"spotify:track:{song['spotify_id']}"
                    similar_songs.append(song)
                    
                except Exception as e:
                    print(f"Error processing embedding for song {song['id']}: {e}")
                    continue
            
            conn.close()
            
            # Sort by similarity score (highest first) and return top n
            similar_songs.sort(key=lambda x: x['match_score'], reverse=True)
            return similar_songs[:n]
            
        except Exception as e:
            print(f"Error in similar songs search: {e}")
            return []

# Tool functions for LangChain agents
def embedding_song_search_tool(query_text: str, n: int = 20) -> List[Dict]:
    """Tool function for embedding-based song search."""
    tools = SearchTools()
    return tools.embedding_song_search(query_text, n)

def song_filter_search_tool(filters: Dict, limit: int = 20) -> List[Dict]:
    """Tool function for filter-based song search."""
    tools = SearchTools()
    return tools.song_filter_search(filters, limit)

def search_songs_by_name_tool(song_list: List[Dict]) -> List[Dict]:
    """Tool function for searching songs by name."""
    tools = SearchTools()
    return tools.search_songs_by_name(song_list)

def get_song_embedding_tool(spotify_id: str) -> Optional[List[float]]:
    """Tool function for retrieving song embeddings."""
    tools = SearchTools()
    return tools.get_song_embedding(spotify_id)

def generate_query_embedding_tool(text: str) -> Optional[List[float]]:
    """Tool function for generating query embeddings."""
    tools = SearchTools()
    return tools.generate_query_embedding(text)

def search_songs_like_tool(reference_song: Dict, n: int = 20) -> List[Dict]:
    """Tool function for finding songs similar to a reference song."""
    tools = SearchTools()
    return tools.search_songs_like(reference_song, n)

