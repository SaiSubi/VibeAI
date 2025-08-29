#!/usr/bin/env python3
"""
VibeAI v2 - Batch Song Analysis Helper
This script helps you batch analyze songs with ChatGPT by:
1. Extracting songs in batches
2. Formatting them for ChatGPT
3. Parsing ChatGPT responses back to database
"""

import sqlite3
import json
from typing import List, Dict, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchSongAnalyzer:
    def __init__(self, db_path: str = "song_database.db"):
        self.db_path = db_path
    
    def get_unanalyzed_songs(self, limit: int = 20) -> List[Dict]:
        """Get songs that don't have lyrical_themes yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, spotify_id, title, artist, album, release_year
            FROM songs
            WHERE lyrical_themes IS NULL OR lyrical_themes = ''
            ORDER BY title
            LIMIT ?
        """, (limit,))
        
        songs = []
        for row in cursor.fetchall():
            songs.append({
                "id": row[0],
                "spotify_id": row[1],
                "title": row[2],
                "artist": row[3],
                "album": row[4],
                "release_year": row[5]
            })
        
        conn.close()
        return songs
    
    def format_songs_for_chatgpt(self, songs: List[Dict]) -> str:
        """Format songs into a clean list for ChatGPT"""
        formatted = "IMPORTANT: Please take your time to think carefully about each song. Prioritize accuracy over speed. If you don't know a song well, search the web for all the information you need to provide accurate analysis.\n\n"
        formatted += "**CRITICAL PROCESSING INSTRUCTIONS:**\n"
        formatted += "- Process each song ONE AT A TIME internally\n"
        formatted += "- For each song: research it completely, fill in ALL data fields, then move to the next song\n"
        formatted += "- Do NOT rush through songs or mix up information between songs\n"
        formatted += "- Spend MORE time on songs you're less familiar with\n"
        formatted += "- Only proceed to the next song after completing the current one\n\n"
        formatted += "Please analyze the following songs and provide:\n\n"
        formatted += "1. **Energy Level**: Score from 0-10 (0=very low energy, 10=very high energy)\n"
        formatted += "2. **Emotion Vector**: Provide a numerical vector [Happy, Sad, Angry] where each value is 0-10 (10 being strongest). Example: [8, 2, 1] means very happy, slightly sad, barely angry.\n"
        formatted += "3. **Language**: Primary language of the song (English, Tamil, Hindi, Telugu, Malayalam, Kannada, Punjabi, etc.)\n"
        formatted += "   For songs with multiple languages, use the primary language. Examples: 'My Universe' by Coldplay & BTS → 'English'\n"
        formatted += "4. **Genre**: Primary musical genre (Pop, Rock, Hip-Hop, R&B, Electronic, Country, Jazz, Classical, Folk, Indie, Bollywood, Tamil Film, etc.)\n"
        formatted += "5. **Lyrical Themes**: Select from these 27 themes (can choose multiple):\n"
        formatted += "   - Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup\n"
        formatted += "   - Friendship, Family, Feel Good, Celebrating Life, Carefree, Escape from Life\n"
        formatted += "   - Unhappy with life, Dreaming, Motivational, Reassuring, Confident\n"
        formatted += "   - Insecure, Love Myself, Hate Myself, Reflection/Introspection, Nostalgia\n"
        formatted += "   - Adventure, Home, Solitude, Spirituality\n\n"
        formatted += "6. **Danceability Score**: Rate how easy it is to dance to this song (0-10, where 10=very danceable, 0=not danceable at all)\n"
        formatted += "7. **Theme Scores**: For each selected theme, rate how strongly it applies (1-10, where 10=perfect match). Only score themes you selected.\n"
        formatted += "8. **Popularity Score**: Rate this song's popularity from 1-10 (1=obscure/unknown, 10=global hit/very famous)\n\n"
        formatted += "**CRITICAL RESEARCH GUIDELINES:**\n"
        formatted += "- Get lyrics from official sources first, else from reputable sites like Genius (prefer verified)\n"
        formatted += "- For film songs, also check scene context\n"
        formatted += "- For non-English songs: obtain original script + two translations (literal & idiomatic), cross-check, and explain cultural references\n"
        formatted += "- Interpret meaning using lyrical meaning, reputable press and community consensus\n"
        formatted += "- Require at least 2 credible sources for 'widely agreed' interpretations\n"
        formatted += "- Don't assume music video = meaning unless confirmed by artist or multiple credible sources\n"
        formatted += "- Select lyrical themes only if strongly supported by lyrics/context\n"
        formatted += "- Score attributes (energy, emotions, danceability, popularity) with clear, evidence-based justification\n"
        formatted += "- If you're unsure about ANY song, search the web for its LYRICS and MEANING\n"
        formatted += "- Focus on what the song is actually SAYING, not just the title or video\n"
        formatted += "- For non-English songs (especially Bollywood, Tamil Film, K-pop), research the actual lyrics and translations\n"
        formatted += "- Don't guess based on title or artist name alone - look up the actual song content and lyrics\n"
        formatted += "- Consider cultural context, especially for songs from different regions and languages\n"
        formatted += "- Be precise with theme scores - don't just give high scores to all themes\n"
        formatted += "- Popularity should reflect global/famous recognition, not just your personal knowledge\n"
        formatted += "- Take extra time for songs you're not familiar with - accuracy is more important than speed\n"
        formatted += "- Remember: A song's title can be misleading - always check the actual lyrics and meaning\n\n"
        formatted += "Format your response as JSON for each song:\n"
        formatted += "```json\n"
        formatted += "[\n"
        formatted += "  {\n"
        formatted += '    "song_id": "ID",\n'
        formatted += '    "title": "Song Title",\n'
        formatted += '    "artist": "Artist Name",\n'
        formatted += '    "energy_level": 8,\n'
        formatted += '    "emotion_vector": [happy_score, sad_score, angry_score],\n'
        formatted += '    "language": "Primary Language",\n'
        formatted += '    "genre": "Primary Genre",\n'
        formatted += '    "danceability_score": 7,\n'
        formatted += '    "lyrical_themes": ["theme1", "theme2", "theme3"],\n'
        formatted += '    "theme_scores": {\n'
        formatted += '      "theme1": 9,\n'
        formatted += '      "theme2": 7,\n'
        formatted += '      "theme3": 8\n'
        formatted += '    },\n'
        formatted += '    "popularity_score": 8\n'
        formatted += '  }\n'
        formatted += "]\n"
        formatted += "```\n\n"
        formatted += "**Songs to analyze:**\n\n"
        
        for i, song in enumerate(songs, 1):
            formatted += f"{i}. **{song['title']}** by {song['artist']}"
            if song['album']:
                formatted += f" (Album: {song['album']}"
                if song['release_year']:
                    formatted += f", {song['release_year']}"
                formatted += ")"
            formatted += "\n"
        
        return formatted
    
    def parse_chatgpt_response(self, response_text: str) -> List[Dict]:
        """Parse ChatGPT's JSON response back to structured data"""
        try:
            # Extract JSON from the response (handle markdown code blocks)
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                # Try to find JSON array directly
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                json_str = response_text[start:end]
            
            parsed_data = json.loads(json_str)
            logger.info(f"✅ Successfully parsed {len(parsed_data)} song analyses")
            return parsed_data
            
        except Exception as e:
            logger.error(f"❌ Failed to parse ChatGPT response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return []
    
    def update_songs_with_analysis(self, analyses: List[Dict]):
        """Update the database with ChatGPT analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated_count = 0
        
        for analysis in analyses:
            try:
                # Create the analysis JSON
                analysis_json = {
                    "energy_level": analysis.get("energy_level", 0),
                    "emotion_vector": analysis.get("emotion_vector", [0, 0, 0]),
                    "language": analysis.get("language", "Unknown"),
                    "genre": analysis.get("genre", "Unknown"),
                    "danceability_score": analysis.get("danceability_score", 0),
                    "lyrical_themes": analysis.get("lyrical_themes", []),
                    "theme_scores": analysis.get("theme_scores", {}),
                    "popularity_score": analysis.get("popularity_score", 0)
                }
                
                # Update the database
                emotion_vector = analysis.get("emotion_vector", [0, 0, 0])
                if isinstance(emotion_vector, list) and len(emotion_vector) == 3:
                    emotion_str = f"{emotion_vector[0]},{emotion_vector[1]},{emotion_vector[2]}"
                else:
                    emotion_str = "0,0,0"
                
                cursor.execute("""
                    UPDATE songs 
                    SET lyrical_themes = ?, mood_tags = ?, energy_level = ?, popularity_score = ?, language = ?, danceability_score = ?
                    WHERE title = ? AND artist = ?
                """, (
                    json.dumps(analysis_json),
                    f"{emotion_str}|{analysis.get('genre', 'Unknown')}",
                    analysis.get("energy_level", 0),
                    analysis.get("popularity_score", 0),
                    analysis.get("language", "Unknown"),
                    analysis.get("danceability_score", 0),
                    analysis["title"],
                    analysis["artist"]
                ))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                    logger.info(f"✅ Updated: {analysis['title']} by {analysis['artist']}")
                else:
                    logger.warning(f"⚠️ No match found for: {analysis['title']} by {analysis['artist']}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to update {analysis.get('title', 'Unknown')}: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"🎉 Updated {updated_count} songs in database")
    
    def get_analysis_progress(self) -> Dict:
        """Get progress on song analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total songs
        cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = cursor.fetchone()[0]
        
        # Analyzed songs
        cursor.execute("SELECT COUNT(*) FROM songs WHERE lyrical_themes IS NOT NULL AND lyrical_themes != ''")
        analyzed_songs = cursor.fetchone()[0]
        
        # Songs with mood tags
        cursor.execute("SELECT COUNT(*) FROM songs WHERE mood_tags IS NOT NULL AND mood_tags != ''")
        mood_tagged_songs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_songs": total_songs,
            "analyzed_songs": analyzed_songs,
            "mood_tagged_songs": mood_tagged_songs,
            "progress_percentage": round((analyzed_songs / total_songs) * 100, 1) if total_songs > 0 else 0
        }

def main():
    """Main function to help with batch analysis"""
    print("🎵 VibeAI v2 - Batch Song Analysis Helper")
    print("=" * 50)
    
    analyzer = BatchSongAnalyzer()
    
    # Show current progress
    progress = analyzer.get_analysis_progress()
    print(f"\n📊 Current Progress:")
    print(f"Total songs: {progress['total_songs']}")
    print(f"Analyzed: {progress['analyzed_songs']} ({progress['progress_percentage']}%)")
    print(f"With mood tags: {progress['mood_tagged_songs']}")
    
    # Get next batch of songs to analyze
    batch_size = 25  # Increased batch size
    unanalyzed = analyzer.get_unanalyzed_songs(batch_size)
    
    if not unanalyzed:
        print("\n🎉 All songs have been analyzed!")
        return
    
    print(f"\n📝 Next batch of {len(unanalyzed)} songs to analyze:")
    for song in unanalyzed:
        print(f"  - {song['title']} by {song['artist']}")
    
    # Format for ChatGPT
    chatgpt_prompt = analyzer.format_songs_for_chatgpt(unanalyzed)
    
    print(f"\n📋 Copy this prompt to ChatGPT:")
    print("=" * 50)
    print(chatgpt_prompt)
    print("=" * 50)
    
    # Option to parse response
    print(f"\n💡 After getting ChatGPT's response, you can:")
    print(f"1. Save the response to a file (e.g., 'chatgpt_response.txt')")
    print(f"2. Run: python v2/batch_analyze_songs.py --parse chatgpt_response.txt")
    print(f"3. Or paste the response directly when prompted")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--parse":
        if len(sys.argv) > 2:
            file_path = sys.argv[2]
            try:
                with open(file_path, 'r') as f:
                    response_text = f.read()
                
                analyzer = BatchSongAnalyzer()
                analyses = analyzer.parse_chatgpt_response(response_text)
                
                if analyses:
                    print(f"📝 Parsed {len(analyses)} song analyses")
                    update = input("Update database with these results? (y/n): ")
                    if update.lower() == 'y':
                        analyzer.update_songs_with_analysis(analyses)
                        print("✅ Database updated!")
                    else:
                        print("❌ Database update cancelled")
                else:
                    print("❌ No valid analyses found in response")
                    
            except FileNotFoundError:
                print(f"❌ File not found: {file_path}")
        else:
            print("❌ Please provide a file path: python v2/batch_analyze_songs.py --parse <file>")
    else:
        main()
