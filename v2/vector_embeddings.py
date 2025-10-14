#!/usr/bin/env python3
"""
VibeAI v2 - Vector Embeddings for Song Search
This module handles generating and managing vector embeddings for songs using Gemini's embedding model.
"""

import psycopg2
import psycopg2.extras
import json
import numpy as np
import google.generativeai as genai
import sys
import os
from typing import List, Dict, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Gemini_API_KEY, DATABASE_URL

class VectorEmbeddingManager:
    def __init__(self, db_url: str = None):
        if db_url is None:
            self.db_url = DATABASE_URL
        else:
            self.db_url = db_url
        self.init_gemini()
    
    def init_gemini(self):
        """Initialize Gemini API for embeddings"""
        genai.configure(api_key=Gemini_API_KEY)
        # Use Gemini's embedding model
        self.embedding_model = 'models/embedding-001'
    
    def create_song_text_representation(self, song: Dict) -> str:
        """
        Create a comprehensive text representation of a song for embedding generation
        
        Args:
            song: Dictionary containing song data
            
        Returns:
            String representation of the song
        """
        # Extract basic info
        title = song.get('title', 'Unknown')
        artist = song.get('artist', 'Unknown')
        album = song.get('album', 'Unknown')
        release_year = song.get('release_year', '')
        genre = song.get('genre', 'Unknown')
        language = song.get('language', 'Unknown')
        
        # Extract analysis data
        energy_level = song.get('energy_level', 0)
        danceability_score = song.get('danceability_score', 0)
        tempo = song.get('tempo', 0)
        melodic_expressiveness = song.get('melodic_expressiveness', 0)
        vocal_prominence = song.get('vocal_prominence', 0)
        timbre = song.get('timbre', 0)
        acousticness = song.get('acousticness', 0)
        popularity_score = song.get('popularity_score', 0)
        
        # Extract mood/emotion data
        mood_tags = song.get('mood_tags', '')
        if mood_tags:
            try:
                # Parse mood tags (format: "happy,sad,angry")
                mood_parts = mood_tags.split(',')
                if len(mood_parts) >= 3:
                    happy_score = mood_parts[0].strip()
                    sad_score = mood_parts[1].strip()
                    angry_score = mood_parts[2].strip()
                    mood_description = f"Emotional characteristics: Happy {happy_score}/10, Sad {sad_score}/10, Angry {angry_score}/10"
                else:
                    mood_description = f"Mood: {mood_tags}"
            except:
                mood_description = f"Mood: {mood_tags}"
        else:
            mood_description = ""
        
        # Extract lyrical themes
        lyrical_themes = song.get('lyrical_themes', '')
        if lyrical_themes:
            try:
                # Try to parse as JSON first
                themes_list = json.loads(lyrical_themes)
                if isinstance(themes_list, list):
                    themes_text = ', '.join(themes_list)
                else:
                    themes_text = lyrical_themes
            except:
                # If not JSON, treat as comma-separated string
                themes_text = lyrical_themes
            themes_description = f"Themes: {themes_text}"
        else:
            themes_description = ""
        
        # Extract song description
        song_description = song.get('song_description', '')
        
        # Build comprehensive text representation
        text_parts = [
            f"Song: {title}",
            f"Artist: {artist}",
            f"Album: {album}",
            f"Year: {release_year}" if release_year else "",
            f"Genre: {genre}",
            f"Language: {language}",
            f"Energy Level: {energy_level}/10",
            f"Danceability: {danceability_score}/10",
            f"Tempo: {tempo}/10",
            f"Melodic Expressiveness: {melodic_expressiveness}/10",
            f"Vocal Prominence: {vocal_prominence}/10",
            f"Timbre: {timbre}/10",
            f"Acousticness: {acousticness}/10",
            f"Popularity: {popularity_score}/10",
            mood_description,
            themes_description,
            song_description
        ]
        
        # Filter out empty parts and join
        text_representation = " | ".join([part for part in text_parts if part.strip()])
        return text_representation
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate vector embedding for given text using Gemini
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of float values representing the embedding, or None if failed
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None
    
    def generate_song_embedding(self, song: Dict) -> Optional[List[float]]:
        """
        Generate embedding for a song based on its metadata
        
        Args:
            song: Dictionary containing song data
            
        Returns:
            List of float values representing the embedding, or None if failed
        """
        text_representation = self.create_song_text_representation(song)
        return self.generate_embedding(text_representation)
    
    def save_song_embedding(self, song_id: int, embedding: List[float]) -> bool:
        """
        Save song embedding to database
        
        Args:
            song_id: Database ID of the song
            embedding: Vector embedding as list of floats
            
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Convert embedding to JSON string for storage
            embedding_json = json.dumps(embedding)
            
            cursor.execute("""
                UPDATE songs SET vector_embedding = ? WHERE id = ?
            """, (embedding_json, song_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error saving embedding for song {song_id}: {e}")
            return False
        finally:
            conn.close()
    
    def get_song_embedding(self, song_id: int) -> Optional[List[float]]:
        """
        Retrieve song embedding from database
        
        Args:
            song_id: Database ID of the song
            
        Returns:
            List of float values representing the embedding, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT vector_embedding FROM songs WHERE id = ?", (song_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving embedding for song {song_id}: {e}")
            return None
        finally:
            conn.close()
    
    def get_songs_without_embeddings(self, limit: int = 50) -> List[Dict]:
        """
        Get songs that don't have embeddings yet
        
        Args:
            limit: Maximum number of songs to return
            
        Returns:
            List of song dictionaries
        """
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT id, title, artist, album, release_year, energy_level, 
                   mood_tags, language, genre, lyrical_themes, danceability_score,
                   tempo, melodic_expressiveness, vocal_prominence, timbre,
                   acousticness, popularity_score, song_description
            FROM songs 
            WHERE vector_embedding IS NULL OR vector_embedding = ''
            ORDER BY id
            LIMIT ?
        """, (limit,))
        
        songs = []
        for row in cursor.fetchall():
            songs.append(dict(row))
        
        conn.close()
        return songs
    
    def generate_embeddings_for_songs(self, limit: int = 50) -> Dict:
        """
        Generate embeddings for songs that don't have them yet
        
        Args:
            limit: Maximum number of songs to process
            
        Returns:
            Dictionary with processing results
        """
        print(f"🔄 Generating embeddings for songs...")
        print("=" * 60)
        
        # Get songs without embeddings
        songs = self.get_songs_without_embeddings(limit)
        
        if not songs:
            print("✅ All songs already have embeddings!")
            return {"processed": 0, "errors": 0, "total": 0}
        
        print(f"📊 Found {len(songs)} songs without embeddings")
        print(f"⚡ Processing without rate limiting (fast mode)")
        print(f"⏰ Estimated time: ~{len(songs) * 0.1 / 60:.1f} minutes")
        print("=" * 60)
        
        processed_count = 0
        error_count = 0
        start_time = time.time()
        
        for i, song in enumerate(songs, 1):
            print(f"\n[{i}/{len(songs)}] Processing: {song['title']} by {song['artist']}")
            
            # Generate embedding
            embedding = self.generate_song_embedding(song)
            
            if embedding:
                # Save to database
                success = self.save_song_embedding(song['id'], embedding)
                
                if success:
                    print(f"   ✅ Successfully generated and stored embedding")
                    processed_count += 1
                else:
                    print(f"   ❌ Failed to save embedding")
                    error_count += 1
            else:
                print(f"   ❌ Failed to generate embedding")
                error_count += 1
            
            # No rate limiting - process as fast as possible
            # Note: This may hit API rate limits, but we'll handle errors gracefully
        
        # Final summary
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 EMBEDDING GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total songs processed: {len(songs)}")
        print(f"✅ Successfully processed: {processed_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        
        return {
            "processed": processed_count,
            "errors": error_count,
            "total": len(songs)
        }
    
    def search_similar_songs(self, query_text: str, limit: int = 20) -> List[Dict]:
        """
        Search for songs similar to the query using vector similarity
        
        Args:
            query_text: Natural language query
            limit: Maximum number of results to return
            
        Returns:
            List of similar songs with similarity scores
        """
        print(f"🔍 Searching for songs similar to: '{query_text}'")
        
        # Generate embedding for query
        query_embedding = self.generate_embedding(query_text)
        if not query_embedding:
            print("❌ Failed to generate query embedding")
            return []
        
        # Get all songs with embeddings
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT id, spotify_id, title, artist, album, release_year, energy_level, 
                   mood_tags, language, genre, lyrical_themes, danceability_score,
                   tempo, melodic_expressiveness, vocal_prominence, timbre,
                   acousticness, popularity_score, song_description, vector_embedding
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
                similarity = cosine_similarity(
                    [query_embedding], 
                    [song_embedding]
                )[0][0]
                
                song['similarity_score'] = float(similarity)
                songs_with_similarities.append(song)
                
            except Exception as e:
                print(f"❌ Error processing embedding for song {song['id']}: {e}")
                continue
        
        conn.close()
        
        # Sort by similarity score (highest first)
        songs_with_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Return top results
        results = songs_with_similarities[:limit]
        
        print(f"📊 Found {len(results)} similar songs")
        return results
    
    def get_embedding_stats(self) -> Dict:
        """Get statistics about embeddings in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total songs
        cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = cursor.fetchone()[0]
        
        # Songs with embeddings
        cursor.execute("SELECT COUNT(*) FROM songs WHERE vector_embedding IS NOT NULL AND vector_embedding != ''")
        songs_with_embeddings = cursor.fetchone()[0]
        
        # Songs without embeddings
        songs_without_embeddings = total_songs - songs_with_embeddings
        
        conn.close()
        
        return {
            "total_songs": total_songs,
            "songs_with_embeddings": songs_with_embeddings,
            "songs_without_embeddings": songs_without_embeddings,
            "embedding_coverage": (songs_with_embeddings / total_songs * 100) if total_songs > 0 else 0
        }

def main():
    """Example usage of VectorEmbeddingManager"""
    print("🎵 VibeAI v2 - Vector Embedding Manager")
    print("=" * 50)
    
    # Initialize manager
    manager = VectorEmbeddingManager()
    
    # Show current stats
    stats = manager.get_embedding_stats()
    print(f"📊 Embedding Stats:")
    print(f"   Total songs: {stats['total_songs']}")
    print(f"   With embeddings: {stats['songs_with_embeddings']}")
    print(f"   Without embeddings: {stats['songs_without_embeddings']}")
    print(f"   Coverage: {stats['embedding_coverage']:.1f}%")
    
    # Example: Generate embeddings for 10 songs
    if stats['songs_without_embeddings'] > 0:
        print(f"\n🔄 Generating embeddings for 10 songs...")
        results = manager.generate_embeddings_for_songs(limit=10)
        print(f"✅ Processing complete: {results['processed']} processed, {results['errors']} errors")
    
    # Example: Search with vector similarity
    if stats['songs_with_embeddings'] > 0:
        print(f"\n🔍 Testing vector search...")
        similar_songs = manager.search_similar_songs("happy energetic songs", limit=5)
        
        print(f"\n🎵 Top similar songs:")
        for i, song in enumerate(similar_songs, 1):
            print(f"{i}. {song['title']} - {song['artist']} (similarity: {song['similarity_score']:.3f})")

if __name__ == "__main__":
    main()
