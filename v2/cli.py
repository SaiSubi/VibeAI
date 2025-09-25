#!/usr/bin/env python3
"""
VibeAI v2 - Command Line Interface
Simple CLI for managing songs and playlists.
"""

import sys
from song_manager import SongManager

def main():
    """Main CLI interface"""
    print("🎵 VibeAI v2 - Song Manager CLI")
    print("=" * 50)
    
    manager = SongManager()
    
    while True:
        print("\n📋 Available Commands:")
        print("1. Show database stats")
        print("2. Import playlist from Spotify")
        print("3. Import playlist from URL")
        print("4. Analyze unanalyzed songs")
        print("5. Find duplicates")
        print("6. Remove duplicates")
        print("7. Search songs (natural language)")
        print("8. Exit")
        
        choice = input("\n🎤 Choose an option (1-8): ").strip()
        
        if choice == "1":
            show_stats(manager)
        elif choice == "2":
            import_playlist(manager)
        elif choice == "3":
            import_playlist_from_url(manager)
        elif choice == "4":
            analyze_songs(manager)
        elif choice == "5":
            find_duplicates(manager)
        elif choice == "6":
            remove_duplicates(manager)
        elif choice == "7":
            search_songs(manager)
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def show_stats(manager):
    """Show database statistics"""
    stats = manager.get_database_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Total songs: {stats['total_songs']}")
    print(f"   Analyzed: {stats['analyzed_songs']}")
    print(f"   Unanalyzed: {stats['unanalyzed_songs']}")
    print(f"   Unique artists: {stats['unique_artists']}")
    print(f"   Duplicates: {stats['duplicates']} ({stats['duplicate_groups']} groups)")

def import_playlist(manager):
    """Import playlist from Spotify"""
    print("\n🎵 Import Playlist from Spotify")
    print("=" * 40)
    
    playlist_names = input("Enter playlist names (comma-separated, or press Enter for all): ").strip()
    playlist_list = [name.strip() for name in playlist_names.split(",")] if playlist_names else None
    
    print("🔄 Importing...")
    results = manager.import_playlist_from_spotify(playlist_names=playlist_list)
    
    if "error" in results:
        print(f"❌ Import failed: {results['error']}")
    else:
        print(f"✅ Import complete:")
        print(f"   Total found: {results['total_found']}")
        print(f"   Unique tracks: {results['unique_tracks']}")
        print(f"   New songs saved: {results['saved']}")
        print(f"   Duplicates skipped: {results['duplicates']}")

def analyze_songs(manager):
    """Analyze unanalyzed songs"""
    print("\n🔄 Analyze Songs")
    print("=" * 40)
    
    limit = input("How many songs to analyze? (default 10): ").strip()
    limit = int(limit) if limit.isdigit() else 10
    
    print(f"🔄 Analyzing {limit} songs...")
    results = manager.analyze_playlist_songs(limit=limit)
    
    print(f"✅ Analysis complete:")
    print(f"   Analyzed: {results['analyzed']}")
    print(f"   Errors: {results['errors']}")
    print(f"   Total processed: {results['total']}")

def find_duplicates(manager):
    """Find duplicate songs"""
    print("\n🔍 Finding Duplicates")
    print("=" * 40)
    
    duplicates = manager.find_duplicates()
    
    if not duplicates:
        print("✅ No duplicates found!")
        return
    
    print(f"📊 Found {len(duplicates)} duplicate groups:")
    for i, dup in enumerate(duplicates[:10], 1):  # Show first 10
        print(f"   {i}. {dup['title']} by {dup['artist']} ({dup['count']} copies)")
    
    if len(duplicates) > 10:
        print(f"   ... and {len(duplicates) - 10} more groups")

def remove_duplicates(manager):
    """Remove duplicate songs"""
    print("\n🗑️  Remove Duplicates")
    print("=" * 40)
    
    keep_analyzed = input("Keep analyzed versions? (y/n, default y): ").strip().lower()
    keep_analyzed = keep_analyzed != 'n'
    
    print("🔄 Removing duplicates...")
    removed = manager.remove_duplicates(keep_analyzed=keep_analyzed)
    
    print(f"✅ Removed {removed} duplicate songs")

def search_songs(manager):
    """Search songs using natural language"""
    print("\n🔍 Search Songs")
    print("=" * 40)
    
    query = input("What songs are you looking for? ").strip()
    if not query:
        return
    
    # Import search function
    from song_search import SongSearchEngine
    search_engine = SongSearchEngine()
    
    songs = search_engine.search_with_natural_language(query)
    search_engine.display_results(songs, query)

def import_playlist_from_url(manager):
    """Import playlist from Spotify URL"""
    print("\n🎵 Import Playlist from URL")
    print("=" * 40)
    
    url = input("Enter Spotify playlist URL or ID: ").strip()
    if not url:
        return
    
    print("🔄 Importing playlist...")
    results = manager.get_playlist_from_url(url)
    
    if "error" in results:
        print(f"❌ Import failed: {results['error']}")
    else:
        print(f"✅ Import complete:")
        print(f"   Total found: {results['total_found']}")
        print(f"   New songs saved: {results['saved']}")
        print(f"   Duplicates skipped: {results['duplicates']}")
        print(f"   Playlist ID: {results['playlist_id']}")

if __name__ == "__main__":
    main()
