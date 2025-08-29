#!/usr/bin/env python3
"""
VibeAI v2 - Interactive Song Analysis
Interactive script to paste ChatGPT responses and update database
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch_analyze_songs import BatchSongAnalyzer

def interactive_analysis():
    """Interactive mode for pasting ChatGPT responses"""
    print("🎵 VibeAI v2 - Interactive Song Analysis")
    print("=" * 50)
    
    analyzer = BatchSongAnalyzer()
    
    # Show current progress
    progress = analyzer.get_analysis_progress()
    print(f"\n📊 Current Progress:")
    print(f"Total songs: {progress['total_songs']}")
    print(f"Analyzed: {progress['analyzed_songs']} ({progress['progress_percentage']}%)")
    print(f"With mood tags: {progress['mood_tagged_songs']}")
    
    while True:
        print(f"\n" + "="*50)
        print("Options:")
        print("1. Get next batch for ChatGPT")
        print("2. Paste ChatGPT response and update database")
        print("3. Show analysis progress")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Get next batch
            batch_size = 25
            unanalyzed = analyzer.get_unanalyzed_songs(batch_size)
            
            if not unanalyzed:
                print("\n🎉 All songs have been analyzed!")
                continue
            
            print(f"\n📝 Next batch of {len(unanalyzed)} songs to analyze:")
            for song in unanalyzed:
                print(f"  - {song['title']} by {song['artist']}")
            
            chatgpt_prompt = analyzer.format_songs_for_chatgpt(unanalyzed)
            
            print(f"\n📋 Copy this prompt to ChatGPT:")
            print("=" * 50)
            print(chatgpt_prompt)
            print("=" * 50)
            
        elif choice == "2":
            # Paste response
            print("\n📝 Paste the ChatGPT response below (press Ctrl+D when done):")
            print("(Or type 'cancel' to go back)")
            
            lines = []
            try:
                while True:
                    line = input()
                    if line.strip() == "cancel":
                        print("❌ Cancelled")
                        break
                    lines.append(line)
            except EOFError:
                pass
            
            if lines:
                response_text = "\n".join(lines)
                
                print(f"\n🔍 Parsing ChatGPT response...")
                analyses = analyzer.parse_chatgpt_response(response_text)
                
                if analyses:
                    print(f"✅ Successfully parsed {len(analyses)} song analyses")
                    print(f"\n📋 Preview of analyses:")
                    for analysis in analyses[:3]:  # Show first 3
                                            print(f"  - {analysis['title']} by {analysis['artist']}")
                    print(f"    Energy: {analysis.get('energy_level', 'N/A')}")
                    emotion_vec = analysis.get('emotion_vector', [0, 0, 0])
                    if isinstance(emotion_vec, list) and len(emotion_vec) == 3:
                        print(f"    Emotion: [Happy: {emotion_vec[0]}, Sad: {emotion_vec[1]}, Angry: {emotion_vec[2]}]")
                    else:
                        print(f"    Emotion: {emotion_vec}")
                    print(f"    Genre: {analysis.get('genre', 'N/A')}")
                    print(f"    Themes: {', '.join(analysis.get('lyrical_themes', []))}")
                    print()
                    
                    if len(analyses) > 3:
                        print(f"  ... and {len(analyses) - 3} more")
                    
                    update = input("Update database with these results? (y/n): ").strip().lower()
                    if update == 'y':
                        analyzer.update_songs_with_analysis(analyses)
                        print("✅ Database updated successfully!")
                        
                        # Show updated progress
                        progress = analyzer.get_analysis_progress()
                        print(f"\n📊 Updated Progress:")
                        print(f"Analyzed: {progress['analyzed_songs']} ({progress['progress_percentage']}%)")
                    else:
                        print("❌ Database update cancelled")
                else:
                    print("❌ No valid analyses found in response")
                    print("Make sure the response contains valid JSON format")
            
        elif choice == "3":
            # Show progress
            progress = analyzer.get_analysis_progress()
            print(f"\n📊 Current Progress:")
            print(f"Total songs: {progress['total_songs']}")
            print(f"Analyzed: {progress['analyzed_songs']} ({progress['progress_percentage']}%)")
            print(f"With mood tags: {progress['mood_tagged_songs']}")
            
            if progress['analyzed_songs'] > 0:
                # Show some sample analyzed songs
                print(f"\n🎵 Sample analyzed songs:")
                conn = analyzer.db_path
                import sqlite3
                conn = sqlite3.connect(analyzer.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT title, artist, mood_tags, lyrical_themes
                    FROM songs
                    WHERE lyrical_themes IS NOT NULL AND lyrical_themes != ''
                    ORDER BY RANDOM()
                    LIMIT 5
                """)
                
                for row in cursor.fetchall():
                    title, artist, mood_tags, lyrical_themes = row
                    print(f"  - {title} by {artist}")
                    print(f"    Mood: {mood_tags}")
                    if lyrical_themes:
                        try:
                            themes_data = json.loads(lyrical_themes)
                            themes = themes_data.get('lyrical_themes', [])
                            if themes:
                                print(f"    Themes: {', '.join(themes[:3])}")
                        except:
                            pass
                    print()
                
                conn.close()
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    interactive_analysis()
