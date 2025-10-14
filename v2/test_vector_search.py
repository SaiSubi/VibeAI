#!/usr/bin/env python3
"""
VibeAI v2 - Simple Vector Search Test Tool
A simple script to test vector embedding search with specific queries.
"""

import sys
import os
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_embeddings import VectorEmbeddingManager

def test_vector_search(query: str, limit: int = 20):
    """
    Test vector search with a specific query.
    
    Args:
        query: Natural language search query
        limit: Maximum number of results to return
        
    Returns:
        List of songs with similarity scores
    """
    print(f"🎵 VibeAI v2 - Vector Search Test")
    print("=" * 60)
    
    # Initialize vector embedding manager
    vector_manager = VectorEmbeddingManager()
    
    # Check database stats
    stats = vector_manager.get_embedding_stats()
    print(f"📊 Database Stats:")
    print(f"   Total songs: {stats['total_songs']}")
    print(f"   Songs with embeddings: {stats['songs_with_embeddings']}")
    print(f"   Coverage: {stats['embedding_coverage']:.1f}%")
    
    if stats['songs_with_embeddings'] == 0:
        print("❌ No songs have embeddings! Please run generate_all_embeddings.py first.")
        return []
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"📊 Looking for top {limit} matches...")
    
    # Use the existing search method
    songs = vector_manager.search_similar_songs(query, limit)
    
    if not songs:
        print("❌ No songs found!")
        return []
    
    print(f"\n🎵 Top {len(songs)} matches for: '{query}'")
    print("=" * 80)
    
    for i, song in enumerate(songs, 1):
        print(f"{i:2d}. {song['title']} - {song['artist']}")
        print(f"    📊 Match Score: {song['similarity_score']:.4f}")
        
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
        
        print(f"    🎧 Spotify URI: spotify:track:{song.get('spotify_id', 'N/A')}")
        print()
    
    # Show some statistics
    avg_score = sum(song['similarity_score'] for song in songs) / len(songs)
    max_score = max(song['similarity_score'] for song in songs)
    min_score = min(song['similarity_score'] for song in songs)
    
    print(f"📈 Statistics:")
    print(f"   Average Score: {avg_score:.4f}")
    print(f"   Highest Score: {max_score:.4f}")
    print(f"   Lowest Score: {min_score:.4f}")
    
    return songs

def main():
    """Main function to run specific test queries."""
    # Test queries to try
    test_queries = [
        "happy energetic songs",
        "sad breakup songs", 
        "workout music",
        "romantic love songs",
        "party dance music",
        "chill relaxing songs",
        "motivational songs",
        "songs for studying",
        "upbeat Hindi songs",
        "rock music with high energy"
    ]
    
    print("🎵 VibeAI v2 - Vector Search Test Tool")
    print("=" * 60)
    print("Available test queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"  {i:2d}. {query}")
    
    print("\nTo test a specific query, run:")
    print("python v2/test_vector_search.py 'your query here'")
    print("\nOr test all queries:")
    print("python v2/test_vector_search.py --all")
    
    # Check if a specific query was provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            print("\n🚀 Testing all queries...")
            for query in test_queries:
                print(f"\n{'='*80}")
                test_vector_search(query, 10)
                print(f"{'='*80}")
        else:
            query = " ".join(sys.argv[1:])
            test_vector_search(query)
    else:
        print("\n💡 Example usage:")
        print("python v2/test_vector_search.py 'happy energetic songs'")

if __name__ == "__main__":
    main()
