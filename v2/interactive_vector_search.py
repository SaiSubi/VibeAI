#!/usr/bin/env python3
"""
VibeAI v2 - Interactive Vector Search Tool
A simple script to test vector embedding search with natural language queries.
"""

import sys
import os
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_embeddings import VectorEmbeddingManager

class InteractiveVectorSearch:
    def __init__(self):
        """Initialize the vector search tool."""
        print("🎵 VibeAI v2 - Interactive Vector Search Tool")
        print("=" * 60)
        
        # Initialize vector embedding manager
        self.vector_manager = VectorEmbeddingManager()
        
        # Check database stats
        stats = self.vector_manager.get_embedding_stats()
        print(f"📊 Database Stats:")
        print(f"   Total songs: {stats['total_songs']}")
        print(f"   Songs with embeddings: {stats['songs_with_embeddings']}")
        print(f"   Coverage: {stats['embedding_coverage']:.1f}%")
        
        if stats['songs_with_embeddings'] == 0:
            print("❌ No songs have embeddings! Please run generate_all_embeddings.py first.")
            sys.exit(1)
        
        print(f"\n✅ Ready to search! Found {stats['songs_with_embeddings']} songs with embeddings.")
        print("=" * 60)
    
    def search_songs(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for songs using vector embeddings.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results to return
            
        Returns:
            List of songs with similarity scores
        """
        print(f"\n🔍 Searching for: '{query}'")
        print(f"📊 Looking for top {limit} matches...")
        
        # Generate embedding for the query
        query_embedding = self.vector_manager.generate_embedding(query)
        if not query_embedding:
            print("❌ Failed to generate embedding for query")
            return []
        
        # Get all songs with embeddings
        import sqlite3
        import json
        from sklearn.metrics.pairwise import cosine_similarity
        
        conn = sqlite3.connect(self.vector_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, artist, album, release_year, energy_level, 
                   mood_tags, language, genre, lyrical_themes, danceability_score,
                   tempo, melodic_expressiveness, vocal_prominence, timbre,
                   acousticness, popularity_score, song_description, vector_embedding, spotify_id
            FROM songs 
            WHERE vector_embedding IS NOT NULL AND vector_embedding != ''
        """)
        
        songs_with_similarities = []
        
        print(f"🔄 Calculating similarities for {cursor.rowcount} songs...")
        
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
                
                # Convert to percentage (0-100)
                match_score = float(similarity) * 100
                
                song['match_score'] = match_score
                song['spotify_uri'] = f"spotify:track:{song['spotify_id']}"
                songs_with_similarities.append(song)
                
            except Exception as e:
                print(f"⚠️  Error processing embedding for song {song['id']}: {e}")
                continue
        
        conn.close()
        
        # Sort by similarity score (highest first) and return top results
        songs_with_similarities.sort(key=lambda x: x['match_score'], reverse=True)
        return songs_with_similarities[:limit]
    
    def display_results(self, songs: List[Dict], query: str):
        """
        Display search results in a formatted way.
        
        Args:
            songs: List of songs with match scores
            query: Original search query
        """
        if not songs:
            print("❌ No songs found!")
            return
        
        print(f"\n🎵 Top {len(songs)} matches for: '{query}'")
        print("=" * 80)
        
        for i, song in enumerate(songs, 1):
            print(f"{i:2d}. {song['title']} - {song['artist']}")
            print(f"    📊 Match Score: {song['match_score']:.1f}%")
            
            # Show additional metadata if available
            metadata_parts = []
            if song.get('album'):
                metadata_parts.append(f"Album: {song['album']}")
            if song.get('release_year'):
                metadata_parts.append(f"Year: {song['release_year']}")
            if song.get('genre'):
                metadata_parts.append(f"Genre: {song['genre']}")
            if song.get('language'):
                metadata_parts.append(f"Language: {song['language']}")
            
            if metadata_parts:
                print(f"    📝 {', '.join(metadata_parts)}")
            
            # Show audio features if available
            features = []
            if song.get('energy_level'):
                features.append(f"Energy: {song['energy_level']}")
            if song.get('tempo'):
                features.append(f"Tempo: {song['tempo']:.0f} BPM")
            if song.get('danceability_score'):
                features.append(f"Danceability: {song['danceability_score']}")
            
            if features:
                print(f"    🎶 {', '.join(features)}")
            
            # Show mood/themes if available
            if song.get('mood_tags'):
                print(f"    😊 Mood: {song['mood_tags']}")
            if song.get('lyrical_themes'):
                print(f"    📝 Themes: {song['lyrical_themes']}")
            
            print(f"    🎧 Spotify URI: {song['spotify_uri']}")
            print()
    
    def run_interactive_search(self):
        """Run the interactive search loop."""
        print("\n🚀 Interactive Vector Search")
        print("Type your queries and see the best matches!")
        print("Commands:")
        print("  - Type any natural language query to search")
        print("  - Type 'quit' or 'exit' to stop")
        print("  - Type 'help' for more options")
        print("-" * 60)
        
        while True:
            try:
                query = input("\n🔍 Enter your search query: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if query.lower() == 'help':
                    self.show_help()
                    continue
                
                if query.lower() == 'stats':
                    self.show_stats()
                    continue
                
                # Perform search
                songs = self.search_songs(query, limit=20)
                
                if songs:
                    self.display_results(songs, query)
                    
                    # Show some statistics
                    avg_score = sum(song['match_score'] for song in songs) / len(songs)
                    max_score = max(song['match_score'] for song in songs)
                    min_score = min(song['match_score'] for song in songs)
                    
                    print(f"📈 Statistics:")
                    print(f"   Average Score: {avg_score:.1f}%")
                    print(f"   Highest Score: {max_score:.1f}%")
                    print(f"   Lowest Score: {min_score:.1f}%")
                else:
                    print("❌ No songs found for this query.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show help information."""
        print("\n📖 Help - Vector Search Tool")
        print("=" * 40)
        print("This tool uses Gemini's vector embeddings to find songs that match")
        print("your natural language queries semantically.")
        print("\nExample queries:")
        print("  • 'happy energetic songs'")
        print("  • 'sad breakup songs'")
        print("  • 'workout music'")
        print("  • 'romantic love songs'")
        print("  • 'party dance music'")
        print("  • 'chill relaxing songs'")
        print("  • 'motivational songs'")
        print("  • 'songs for studying'")
        print("\nCommands:")
        print("  • 'stats' - Show database statistics")
        print("  • 'help' - Show this help")
        print("  • 'quit' - Exit the program")
    
    def show_stats(self):
        """Show database statistics."""
        stats = self.vector_manager.get_embedding_stats()
        print(f"\n📊 Database Statistics")
        print("=" * 30)
        print(f"Total songs: {stats['total_songs']}")
        print(f"Songs with embeddings: {stats['songs_with_embeddings']}")
        print(f"Songs without embeddings: {stats['songs_without_embeddings']}")
        print(f"Coverage: {stats['embedding_coverage']:.1f}%")
        
        if stats['songs_without_embeddings'] > 0:
            print(f"\n💡 Tip: Run 'python generate_all_embeddings.py' to generate")
            print(f"   embeddings for the remaining {stats['songs_without_embeddings']} songs.")

def main():
    """Main function to run the interactive search tool."""
    try:
        search_tool = InteractiveVectorSearch()
        search_tool.run_interactive_search()
    except Exception as e:
        print(f"❌ Error initializing search tool: {e}")
        print("Make sure you have:")
        print("1. Generated embeddings for your songs")
        print("2. Set up your Gemini API key")
        print("3. Have the required dependencies installed")

if __name__ == "__main__":
    main()
