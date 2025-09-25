#!/usr/bin/env python3
"""
Demo script for VibeAI v2 Frontend
Shows how the new combined search function works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from song_search import SongSearchEngine
from song_manager import SongManager

def demo_combined_search():
    """Demo the new combined search functionality"""
    print("🎵 VibeAI v2 Frontend Demo")
    print("=" * 50)
    
    # Initialize search engine
    search_engine = SongSearchEngine()
    song_manager = SongManager()
    
    # Get database stats
    stats = song_manager.get_database_stats()
    print(f"📊 Database Stats:")
    print(f"   Total songs: {stats['total_songs']}")
    print(f"   Analyzed: {stats['analyzed_songs']}")
    print(f"   Unanalyzed: {stats['unanalyzed_songs']}")
    print()
    
    # Demo 1: Natural language search
    print("🔍 Demo 1: Natural Language Search")
    print("Query: 'happy energetic songs'")
    try:
        songs = search_engine.search_with_natural_language("happy energetic songs")
        print(f"Found {len(songs)} songs")
        if songs:
            for i, song in enumerate(songs[:3], 1):
                print(f"  {i}. {song['title']} by {song['artist']}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Demo 2: Combined search with filters
    print("🔍 Demo 2: Combined Search with Filters")
    print("Query: 'romantic songs' + Energy: 3-7 + Themes: Love")
    
    # Build combined query
    combined_query = "romantic songs energy level between 3 and 7 songs with themes: In Love, Hopeful Love"
    try:
        songs = search_engine.search_with_natural_language(combined_query)
        print(f"Found {len(songs)} songs")
        if songs:
            for i, song in enumerate(songs[:3], 1):
                print(f"  {i}. {song['title']} by {song['artist']}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Demo 3: Default playlist query
    print("🔍 Demo 3: Default Playlist Query")
    print("Query: 'moody atmospheric songs for driving at night'")
    try:
        songs = search_engine.search_with_natural_language("moody atmospheric songs for driving at night")
        print(f"Found {len(songs)} songs")
        if songs:
            for i, song in enumerate(songs[:3], 1):
                print(f"  {i}. {song['title']} by {song['artist']}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    print("✅ Demo completed!")
    print()
    print("🚀 To start the frontend:")
    print("   cd frontend")
    print("   python run.py")
    print("   Then open: http://localhost:5001")

if __name__ == "__main__":
    demo_combined_search()
