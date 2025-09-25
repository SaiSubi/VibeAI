# VibeAI v2 - Song Manager

A clean, modular system for managing song databases, analyzing songs with AI, and searching with natural language.

## 🎵 Features

### Core Functions
- **Song Analysis**: Use Google Gemini Flash to analyze songs for energy, emotions, themes, and more
- **Playlist Import**: Import songs from Spotify playlists with duplicate detection
- **Playlist URL Import**: Import songs from any Spotify playlist by URL
- **Batch Processing**: Analyze multiple songs with rate limiting
- **Duplicate Management**: Find and remove duplicate songs
- **Natural Language Search**: Search songs using conversational queries based on database attributes

### Database Schema
The system stores comprehensive song data including:
- Basic info (title, artist, album, year)
- Spotify audio features (energy, danceability, tempo, etc.)
- AI analysis (emotions, themes, language, genre)
- Custom scores (popularity, melodic expressiveness, etc.)

## 🚀 Quick Start

### 1. Basic Usage
```python
from song_manager import SongManager

# Initialize manager
manager = SongManager()

# Show database stats
stats = manager.get_database_stats()
print(f"Total songs: {stats['total_songs']}")

# Analyze 10 unanalyzed songs
results = manager.analyze_playlist_songs(limit=10)
```

### 2. CLI Interface
```bash
python cli.py
```

### 3. Natural Language Search
```python
from song_search import SongSearchEngine

search_engine = SongSearchEngine()
songs = search_engine.search_with_natural_language("happy energetic songs")
```

### 4. Import Playlist from URL
```python
# Import any Spotify playlist by URL
results = manager.get_playlist_from_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

# Or use playlist ID directly
results = manager.get_playlist_from_url("37i9dQZF1DXcBWIGoYBM5M")
```

## 📁 File Structure

```
v2/
├── song_manager.py      # Core functionality
├── song_search.py       # Natural language search
├── cli.py              # Command line interface
├── test_recommendations.py  # Test script for recommendations
├── song_database.db    # SQLite database
└── README.md           # This file
```

## 🔧 Core Functions

### SongManager Class

#### `analyze_song_with_gemini(title, artist)`
Analyze a single song using Gemini API
- Returns: (analysis_data, error_message)

#### `analyze_playlist_songs(playlist_name=None, limit=50)`
Analyze multiple songs with rate limiting
- Handles rate limiting (10 requests/minute)
- Shows progress and statistics

#### `import_playlist_from_spotify(user_id=None, playlist_names=None)`
Import songs from Spotify playlists
- Automatically detects and skips duplicates
- Gets audio features from Spotify API

#### `find_duplicates()`
Find duplicate songs in database
- Groups by title and artist (case-insensitive)

#### `remove_duplicates(keep_analyzed=True)`
Remove duplicate songs
- Option to keep analyzed versions

#### `get_playlist_from_url(playlist_url)`
Import songs from any Spotify playlist by URL
- Accepts full Spotify URLs or playlist IDs
- Automatically extracts playlist ID from URL
- Gets audio features and saves to database

### SongSearchEngine Class

#### `search_with_natural_language(query)`
Convert natural language to database search
- Examples:
  - "happy energetic songs"
  - "sad breakup songs in Hindi"
  - "danceable Bollywood songs"
  - "songs by A.R. Rahman"

## 🎯 Example Queries

### Natural Language Search
- "I want happy, energetic songs"
- "Sad breakup songs in Hindi"
- "Danceable Bollywood songs"
- "Songs by A.R. Rahman"
- "Slow romantic songs"
- "Motivational workout songs"

### CLI Commands
1. Show database stats
2. Import playlist from Spotify
3. Import playlist from URL
4. Analyze unanalyzed songs
5. Find duplicates
6. Remove duplicates
7. Search songs (natural language)
8. Exit

## 🔄 Workflow

1. **Import**: Use `import_playlist_from_spotify()` to add songs
2. **Analyze**: Use `analyze_playlist_songs()` to analyze with AI
3. **Search**: Use natural language search to find songs
4. **Maintain**: Use duplicate detection and removal as needed

## ⚙️ Configuration

The system uses environment variables from `utils/config.py`:
- `Gemini_API_KEY`: For song analysis
- `SPOTIFY_CLIENT_ID`: For Spotify API access
- `SPOTIFY_CLIENT_SECRET`: For Spotify API access
- `VibeAI_userid`: Default user ID for Spotify

## 📊 Database Stats

The system tracks:
- Total songs
- Analyzed vs unanalyzed songs
- Unique artists
- Duplicate songs
- Analysis progress

## 🚨 Rate Limiting

- Gemini API: 10 requests per minute (6-second delay)
- Spotify API: Handled automatically
- Progress shown during batch operations

## 🔍 Search Capabilities

The natural language search understands:
- **Energy levels**: "energetic", "calm", "high energy"
- **Emotions**: "happy", "sad", "angry"
- **Languages**: "English", "Hindi", "Tamil"
- **Genres**: "Pop", "Rock", "Bollywood"
- **Themes**: "love", "breakup", "motivational"
- **Attributes**: "danceable", "melodic", "acoustic"
- **Artists**: "songs by [artist]"
- **Time periods**: "songs from 2020"

## 🛠️ Future Development

The modular structure makes it easy to add:
- New analysis features
- Additional search capabilities
- Different AI models
- Export/import formats
- Web interface
- API endpoints