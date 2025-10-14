#!/usr/bin/env python3
"""
VibeAI v2 - Vector Search Usage Guide
Simple examples of how to use the vector embedding search.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_embeddings import VectorEmbeddingManager

def quick_test():
    """Run a quick test of the vector search."""
    print("🎵 VibeAI v2 - Vector Search Quick Test")
    print("=" * 50)
    
    # Initialize the vector manager
    vector_manager = VectorEmbeddingManager()
    
    # Test queries
    test_queries = [
        "happy energetic songs",
        "sad breakup songs", 
        "workout music",
        "romantic love songs"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 30)
        
        # Get top 5 results
        results = vector_manager.search_similar_songs(query, 5)
        
        if results:
            for i, song in enumerate(results, 1):
                print(f"{i}. {song['title']} - {song['artist']}")
                print(f"   Score: {song['similarity_score']:.4f}")
                if song.get('mood_tags'):
                    print(f"   Mood: {song['mood_tags']}")
                if song.get('lyrical_themes'):
                    print(f"   Themes: {song['lyrical_themes']}")
                print()
        else:
            print("   No results found")

if __name__ == "__main__":
    quick_test()
