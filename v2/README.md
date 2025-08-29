# VibeAI v2 Development

This folder contains the core files for VibeAI v2 development.

## Files

### `build_database.py` (formerly `test.py`)
- Main script for building the enhanced song database
- Fetches user playlists and tracks from Spotify
- Retrieves audio features (when working)
- Saves song metadata to SQLite database
- Handles duplicate detection and error logging

### `query_database.py` (formerly `query_db.py`)
- Script to query and explore the created song database
- Functions to search by mood, artist, and lyrical themes
- Database statistics and analysis
- Example queries for testing

### `batch_analyze_songs.py` (NEW)
- Batch song analysis helper for ChatGPT integration
- Extracts songs in manageable batches (25 songs)
- Formats songs for ChatGPT analysis with structured prompts
- Parses ChatGPT JSON responses and updates database
- Tracks analysis progress

### `interactive_analysis.py` (NEW)
- Interactive script for pasting ChatGPT responses directly
- No need to save files - paste responses directly
- Real-time database updates
- Progress tracking and preview of analyses

### `view_analysis.py` (NEW)
- View and explore analyzed songs
- Search by emotion, energy level, genre, and lyrical themes
- Statistics on analysis distribution
- Interactive querying of results

## Database

The script creates `song_database.db` (SQLite) with the following schema:
- `songs` table with song metadata and Spotify features
- Currently contains 410+ songs from your playlists
- Audio features column is empty due to API 403 error

## Usage

```bash
# Build the database
python v2/build_database.py

# Query the database
python v2/query_database.py

# Batch analyze songs with ChatGPT
python v2/batch_analyze_songs.py

# Interactive analysis (paste ChatGPT responses directly)
python v2/interactive_analysis.py

# View analysis results
python v2/view_analysis.py
```

## ChatGPT Analysis Workflow

1. **Get a batch of songs to analyze:**
   ```bash
   python v2/batch_analyze_songs.py
   ```

2. **Copy the generated prompt to ChatGPT**

3. **Paste ChatGPT's response back:**
   ```bash
   python v2/interactive_analysis.py
   # Choose option 2 and paste the response
   ```

4. **View your analyzed songs:**
   ```bash
   python v2/view_analysis.py
   ```

**Or use file-based approach:**
```bash
# Save ChatGPT response to file
python v2/batch_analyze_songs.py --parse chatgpt_response.txt
```

## Current Status

- ✅ Database building works (410+ songs)
- ✅ Playlist fetching works
- ✅ ChatGPT analysis workflow ready
- ❌ Audio features return 403 error
- 🔄 Ready for agentic filtering system development

## Analysis Features

The system analyzes songs for multiple key traits:

1. **Energy Level**: Numerical score 0-10 (0=very low energy, 10=very high energy)
2. **Emotion Vector**: Numerical vector [Happy, Sad, Angry] with scores 0-10 (10 being strongest)
3. **Language**: Primary language of the song (English, Tamil, Hindi, Telugu, Malayalam, Kannada, Punjabi, etc.)
4. **Genre**: Primary musical genre (Pop, Rock, Hip-Hop, R&B, Electronic, Country, Jazz, Classical, Folk, Indie, Bollywood, Tamil Film, etc.)
5. **Danceability Score**: How easy it is to dance to this song (0-10, where 10=very danceable)
6. **Lyrical Themes**: 27 specific themes including Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup, Friendship, Family, Feel Good, Celebrating Life, Carefree, Escape from Life, Unhappy with life, Dreaming, Motivational, Reassuring, Confident, Insecure, Love Myself, Hate Myself, Reflection/Introspection, Nostalgia, Adventure, Home, Solitude, Spirituality
7. **Theme Scores**: For each selected theme, a score 1-10 indicating how strongly it applies
8. **Popularity Score**: Song's popularity from 1-10 (1=obscure, 10=global hit)

## Next Steps

1. ✅ Add lyrical themes via ChatGPT analysis (WORKFLOW READY)
2. Build agentic filtering system using analyzed data
3. Resolve audio features API issue
4. Integrate with main VibeAI application 