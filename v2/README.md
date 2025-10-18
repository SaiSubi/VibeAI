# VibeAI v2 - Advanced AI-Powered Song Management & Search System

A sophisticated, modular system that combines AI analysis, vector embeddings, and multi-agent search to provide intelligent song discovery and management capabilities.

## 🎵 Core Features

### 🤖 AI-Powered Analysis
- **Gemini 2.5 Flash Integration**: Advanced song analysis using Google's latest AI model
- **Comprehensive Song Profiling**: Energy levels, emotions, themes, language detection, genre classification
- **Intelligent Scoring**: Custom algorithms for popularity, melodic expressiveness, vocal prominence, and more
- **Batch Processing**: Efficient analysis of multiple songs with rate limiting and progress tracking

### 🔍 Advanced Search Capabilities
- **Natural Language Search**: Conversational queries like "happy energetic songs" or "sad breakup songs in Hindi"
- **Vector Embeddings**: Semantic similarity search using Gemini's embedding model for nuanced music discovery
- **Multi-Agent AI System**: 4-agent workflow for complex queries requiring research and intelligent decision-making
- **Hybrid Search**: Combines structured database queries with vector similarity for optimal results
- **Filter-Based Search**: Precise control over energy, tempo, danceability, themes, genres, and more

### 🎧 Playlist Management
- **Spotify Integration**: Import songs from any Spotify playlist by URL or user playlists
- **Duplicate Detection**: Smart identification and removal of duplicate songs
- **Audio Features**: Automatic extraction of Spotify's audio analysis data
- **Playlist Creation**: Generate Spotify playlists directly from search results

### 🗄️ Database Architecture
**PostgreSQL-powered storage** with comprehensive song metadata:
- **Basic Info**: Title, artist, album, release year, duration, popularity
- **Spotify Audio Features**: Energy, danceability, tempo, acousticness, instrumentalness, liveness, loudness, speechiness, key, mode, time signature
- **AI Analysis**: Energy levels, emotion vectors (Happy/Sad/Angry), language, genre, lyrical themes
- **Custom Metrics**: Danceability scores, melodic expressiveness, vocal prominence, timbre, acousticness
- **Vector Embeddings**: High-dimensional representations for semantic search

## 🚀 Quick Start

### 1. Basic Song Management
```python
from song_manager import SongManager

# Initialize manager
manager = SongManager()

# Show database stats
stats = manager.get_database_stats()
print(f"Total songs: {stats['total_songs']}")
print(f"Analyzed: {stats['analyzed_songs']}")
print(f"Unique artists: {stats['unique_artists']}")

# Analyze unanalyzed songs
results = manager.analyze_playlist_songs(limit=10)
```

### 2. Advanced Search Options
```python
from song_search import SongSearchEngine

search_engine = SongSearchEngine()

# Natural language search
songs = search_engine.search_with_natural_language("happy energetic songs")

# Vector similarity search
songs = search_engine.search_with_vector_similarity("workout music", limit=20)

# Hybrid search (combines both approaches)
songs = search_engine.search_with_hybrid_approach("sad breakup songs", vector_weight=0.7)
```

### 3. Multi-Agent AI Search
```python
from agentic_search import agentic_song_search

# Complex queries requiring research and intelligent decision-making
result = agentic_song_search("songs like Bohemian Rhapsody", max_results=10)
print(f"Found {result['total_selected']} songs using {result['search_method']} method")
```

### 4. Playlist Management
```python
# Import from Spotify playlist URL
results = manager.get_playlist_from_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

# Import from user's playlists
results = manager.import_playlist_from_spotify(playlist_names=["My Favorites", "Workout Mix"])

# Find and remove duplicates
duplicates = manager.find_duplicates()
removed = manager.remove_duplicates(keep_analyzed=True)
```

### 5. Web Interface
```bash
# Start the Flask web server
cd frontend
python app.py
# Access at http://localhost:5001
```

### 6. Command Line Interface
```bash
python cli.py
```

## 📁 File Structure

```
v2/
├── song_manager.py           # Core song management and analysis
├── song_search.py           # Natural language and hybrid search
├── agentic_search.py        # Multi-agent AI search system
├── simplified_agentic_search.py  # Simplified agentic search
├── search_tools.py          # Tools for agent-based search
├── vector_embeddings.py     # Vector embedding management
├── cli.py                  # Command line interface
├── frontend/               # Web interface
│   ├── app.py              # Flask API server
│   ├── templates/          # HTML templates
│   ├── static/             # CSS/JS assets
│   └── requirements.txt    # Frontend dependencies
├── song_database.db        # SQLite database (if using SQLite)
└── README.md              # This file
```

## 🔧 Core Components

### SongManager Class
**Central hub for song operations**

#### Key Methods:
- `analyze_song_with_gemini(title, artist)` - AI analysis of individual songs
- `analyze_playlist_songs(limit=50)` - Batch analysis with rate limiting
- `import_playlist_from_spotify()` - Import from user's Spotify playlists
- `get_playlist_from_url(url)` - Import from any Spotify playlist URL
- `find_duplicates()` / `remove_duplicates()` - Duplicate management
- `get_database_stats()` - Database statistics and health metrics

### SongSearchEngine Class
**Advanced search capabilities**

#### Search Methods:
- `search_with_natural_language(query)` - Convert natural language to structured search
- `search_with_vector_similarity(query)` - Semantic similarity using embeddings
- `search_with_hybrid_approach(query)` - Combines structured + vector search
- `parse_natural_language_query(query)` - AI-powered query interpretation

### AgenticSongSearch Class
**Multi-agent AI system for complex queries**

#### Agent Workflow:
1. **Agent 1 (Information Need)**: Analyzes query and determines if research is needed
2. **Agent 2 (Lookup)**: Researches additional information when required
3. **Agent 3 (Search)**: Executes appropriate search strategy using available tools
4. **Agent 4 (Finalizer)**: Ranks and selects final results with reasoning

#### Available Tools:
- `embedding_song_search_tool()` - Vector similarity search
- `song_filter_search_tool()` - Structured database queries
- `search_songs_by_name_tool()` - Exact/fuzzy name matching
- `search_songs_like_tool()` - Similarity to reference songs

### VectorEmbeddingManager Class
**Semantic search using AI embeddings**

#### Key Features:
- `generate_embedding(text)` - Create embeddings for queries
- `create_song_text_representation(song)` - Convert song data to searchable text
- `search_similar_songs(query, limit)` - Find semantically similar songs
- `generate_all_embeddings()` - Batch process songs for embeddings

## 🎯 Search Capabilities & Examples

### Natural Language Queries
The system understands conversational queries and converts them to structured searches:

**Energy & Mood:**
- "happy energetic songs" → High energy + positive emotions
- "sad breakup songs in Hindi" → Low energy + sad emotions + Hindi language
- "motivational workout songs" → High energy + motivational themes

**Genre & Style:**
- "danceable Bollywood songs" → High danceability + Bollywood genre
- "acoustic folk songs" → High acousticness + Folk genre
- "electronic dance music" → Electronic genre + high danceability

**Artist & Time:**
- "songs by A.R. Rahman" → Artist filter
- "songs from the 90s" → Year range 1990-1999
- "recent pop hits" → Recent years + Pop genre + high popularity

**Complex Queries:**
- "slow romantic songs for a date" → Low tempo + romantic themes
- "songs like Bohemian Rhapsody" → Similarity search using reference song
- "Tamil film songs from 2020" → Language + genre + year filters

### Multi-Agent AI Examples
The agentic system handles complex queries requiring research:

**Reference-Based Queries:**
- "songs like [specific song]" → Agent researches song characteristics
- "soundtrack songs from [movie/game]" → Agent finds soundtrack information
- "songs similar to [artist]'s style" → Agent analyzes artist characteristics

**Contextual Queries:**
- "songs for a road trip" → Agent considers energy, tempo, and mood
- "music for studying" → Agent selects instrumental/low-vocal tracks
- "party playlist songs" → Agent focuses on danceability and energy

### Search Methods Comparison

| Method | Best For | Speed | Accuracy | Use Case |
|--------|----------|-------|----------|----------|
| **Natural Language** | Conversational queries | Fast | High | "happy songs", "workout music" |
| **Vector Similarity** | Semantic similarity | Medium | Very High | "songs like X", mood-based search |
| **Hybrid** | Complex queries | Medium | Highest | Best of both worlds |
| **Agentic** | Research-heavy queries | Slow | Highest | "songs from Elden Ring", complex references |

## 🔄 Typical Workflow

### 1. Setup & Import
```python
# Initialize the system
manager = SongManager()

# Import songs from Spotify
results = manager.get_playlist_from_url("https://open.spotify.com/playlist/...")
print(f"Imported {results['saved']} new songs")

# Check database status
stats = manager.get_database_stats()
print(f"Database: {stats['total_songs']} songs, {stats['analyzed_songs']} analyzed")
```

### 2. AI Analysis
```python
# Analyze unanalyzed songs (with rate limiting)
results = manager.analyze_playlist_songs(limit=20)
print(f"Analyzed {results['analyzed']} songs successfully")

# Generate vector embeddings for semantic search
from vector_embeddings import VectorEmbeddingManager
vector_manager = VectorEmbeddingManager()
vector_manager.generate_all_embeddings()
```

### 3. Search & Discovery
```python
# Natural language search
search_engine = SongSearchEngine()
songs = search_engine.search_with_natural_language("happy energetic songs")

# Multi-agent search for complex queries
from agentic_search import agentic_song_search
result = agentic_song_search("songs like Bohemian Rhapsody", max_results=10)
```

### 4. Playlist Creation
```python
# Create Spotify playlist from search results
from frontend.app import create_spotify_playlist
playlist_result = create_spotify_playlist(songs, "My AI-Generated Playlist")
print(f"Created playlist: {playlist_result['playlist_url']}")
```

## ⚙️ Configuration

### Environment Variables
The system uses environment variables from `utils/config.py`:

**Required:**
- `Gemini_API_KEY`: Google Gemini API key for AI analysis and embeddings
- `SPOTIFY_CLIENT_ID`: Spotify API client ID
- `SPOTIFY_CLIENT_SECRET`: Spotify API client secret
- `DATABASE_URL`: PostgreSQL connection string

**Optional:**
- `VibeAI_userid`: Default Spotify user ID for playlist operations
- `FRONTEND_URL`: Frontend URL for CORS configuration
- `ALLOWED_ORIGINS`: Allowed origins for API access

### Database Setup
**PostgreSQL (Recommended):**
```sql
-- The system automatically creates the songs table with:
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    spotify_id TEXT UNIQUE,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    release_year INTEGER,
    -- ... comprehensive metadata fields
    vector_embedding TEXT DEFAULT NULL
);
```

**SQLite (Alternative):**
- Automatically handled by the system
- File: `song_database.db`

### Rate Limiting
- **Gemini API**: 10 requests/minute (6-second delay between requests)
- **Spotify API**: Handled automatically with retry logic
- **Batch Operations**: Progress tracking and error handling

## 🌐 Web Interface

### Flask API Server
The web interface provides a modern, responsive frontend for song discovery:

**Features:**
- **Interactive Search**: Real-time search with multiple methods
- **Advanced Filters**: Energy, tempo, danceability, themes, genres, languages
- **Predefined Playlists**: Curated playlists for different moods and activities
- **Spotify Integration**: Direct playlist creation from search results
- **Responsive Design**: Works on desktop and mobile devices

**API Endpoints:**
- `POST /api/search` - Search songs with natural language and filters
- `POST /api/agentic-search` - Multi-agent AI search
- `GET /api/languages` - Get available languages for filtering
- `GET /api/artists` - Get artist list for autocomplete
- `GET /api/playlists` - Get predefined playlist templates
- `POST /api/create-spotify-playlist` - Create Spotify playlist from results

### Predefined Playlists
The system includes 10 curated playlist templates:
- **Late Night Drive**: Moody atmospheric songs
- **Workout Energy**: High-energy motivational tracks
- **Romantic Evening**: Slow romantic love songs
- **Party Time**: Danceable party songs
- **Chill Vibes**: Relaxing unwind music
- **Road Trip**: Upbeat adventure songs
- **Coffee Shop Jazz**: Smooth acoustic background music
- **Rainy Day**: Melancholic introspective tracks
- **Focus Flow**: Instrumental ambient music
- **Sunset Vibes**: Warm mellow evening songs

## 📊 Performance & Scalability

### Database Performance
- **PostgreSQL**: Optimized for large-scale music databases
- **Indexing**: Automatic indexing on frequently searched fields
- **Vector Search**: Efficient similarity search using cosine similarity
- **Batch Operations**: Optimized for bulk imports and analysis

### AI Processing
- **Rate Limiting**: Respects API limits with intelligent queuing
- **Error Handling**: Robust error recovery and retry mechanisms
- **Progress Tracking**: Real-time feedback during long operations
- **Caching**: Intelligent caching of AI analysis results

### Search Performance
- **Multiple Strategies**: Choose optimal search method for query type
- **Hybrid Approach**: Combines speed of structured search with accuracy of vector search
- **Result Ranking**: Intelligent scoring based on relevance and quality
- **Pagination**: Efficient handling of large result sets

## 🛠️ Development & Extensibility

### Modular Architecture
The system is designed for easy extension and customization:

**Core Modules:**
- `song_manager.py` - Central song operations
- `song_search.py` - Search algorithms and query processing
- `agentic_search.py` - Multi-agent AI system
- `vector_embeddings.py` - Semantic search capabilities
- `search_tools.py` - Tool functions for agents

**Easy Extensions:**
- **New AI Models**: Replace Gemini with other AI providers
- **Additional Search Methods**: Implement new search algorithms
- **Custom Metrics**: Add new song analysis dimensions
- **Export Formats**: Support additional playlist formats
- **API Integrations**: Connect to other music services

### Testing & Quality
- **Comprehensive Error Handling**: Graceful failure recovery
- **Input Validation**: Robust validation of user inputs
- **Logging**: Detailed logging for debugging and monitoring
- **Type Hints**: Full type annotation for better code quality

## 🚀 Future Roadmap

### Planned Features
- **Real-time Collaboration**: Multi-user playlist creation
- **Machine Learning**: Personalized recommendations based on user preferences
- **Advanced Analytics**: Music trend analysis and insights
- **Mobile App**: Native mobile application
- **Social Features**: Share playlists and discover music from friends
- **Voice Search**: Voice-activated song discovery
- **Integration APIs**: Connect with more music streaming services

### Technical Improvements
- **Performance Optimization**: Faster search algorithms
- **Scalability**: Support for millions of songs
- **Advanced AI**: Integration with latest AI models
- **Real-time Updates**: Live playlist updates and synchronization