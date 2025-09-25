# VibeAI v2 - Enhanced Song Analysis & Recommendation System

A comprehensive music analysis platform that uses LLMs (ChatGPT and Gemini) to analyze songs and create intelligent music recommendations based on detailed metadata analysis.

## 🎵 Analysis Features

The system analyzes songs across **12 comprehensive dimensions**:

### Core Musical Attributes
- **Energy Level** (0-10): Overall energy and intensity of the song
- **Danceability Score** (0-10): How easy it is to dance to the song
- **Tempo**: Musical speed (BPM) from Spotify data
- **Acousticness**: How acoustic vs. electronic the song is

### Emotional & Thematic Analysis
- **Emotion Vector** [Happy, Sad, Angry]: Numerical scores (0-10) for each emotion
- **Lyrical Themes**: Up to 5 themes selected from 27 options including:
  - Love & Relationships: Hopeful Love, In Love, Lust, Toxic Relationship, Flirty, Longing, Breakup
  - Life & Emotions: Feel Good, Celebrating Life, Carefree, Escape from Life, Unhappy with life, Dreaming
  - Personal Growth: Motivational, Reassuring, Confident, Insecure, Love Myself, Hate Myself
  - Reflection & Spirituality: Reflection/Introspection, Nostalgia, Spirituality
  - Adventure & Home: Adventure, Home, Solitude

### Musical Quality & Character
- **Melodic Expressiveness** (0-10): How melodically expressive the song is
- **Vocal Prominence** (0-10): How prominent vocals are vs. instrumental elements
- **Timbre** (0-10): Overall sound quality and character
- **Theme Scores**: Individual scores (1-10) for each selected lyrical theme

### Context & Recognition
- **Language**: Primary language of the song
- **Genre**: Primary musical genre
- **Popularity Score** (1-10): Global recognition and fame level
- **Song Description**: Brief 1-2 line summary of what the song is about

## 🚀 Key Features

- **LLM-Powered Analysis**: Uses ChatGPT and Gemini for intelligent song interpretation
- **Comprehensive Database**: SQLite database with detailed song metadata
- **Batch Processing**: Analyze up to 25 songs at once
- **Interactive Interface**: Command-line tools for analysis and exploration
- **Advanced Search**: Find songs by emotion, energy, language, genre, themes, and more
- **Research-Based**: LLMs search the web for accurate lyrics and cultural context

## 📁 Project Structure

```
vibeai/
├── v2/                          # Core analysis system
│   ├── build_database.py        # Database initialization
│   ├── batch_analyze_songs.py   # Batch analysis with ChatGPT
│   ├── interactive_analysis.py  # Interactive analysis interface
│   ├── view_analysis.py         # View and search analyzed songs
│   └── test_gemini.py          # Gemini API testing
├── utils/                       # Utility modules
├── scripts/                     # Various utility scripts
└── song_database.db            # SQLite database
```

## 🛠️ Usage

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your Spotify and Gemini API keys
```

### 2. Build Database
```bash
cd v2
python build_database.py
```

### 3. Analyze Songs
```bash
# Get batch for ChatGPT analysis
python batch_analyze_songs.py

# Interactive analysis
python interactive_analysis.py

# View results
python view_analysis.py
```

### 4. Test Gemini Integration
```bash
python test_gemini.py
```

## 🔧 Technical Details

- **Database**: SQLite with comprehensive song metadata
- **LLM Integration**: ChatGPT (manual) + Gemini API (automated)
- **Analysis Workflow**: Research → Analysis → JSON Parsing → Database Update
- **Search Capabilities**: Multi-dimensional filtering and ranking
- **Data Quality**: Research guidelines ensure accuracy and cultural context

## 🎯 Use Cases

- **Music Discovery**: Find songs matching specific moods or themes
- **Playlist Creation**: Build playlists based on emotional or thematic criteria
- **Cultural Research**: Analyze songs across different languages and cultures
- **Music Education**: Understand song structure and lyrical themes
- **Recommendation Systems**: Power AI-driven music recommendations

## 🔮 Future Enhancements

- **Real-time Analysis**: Live song analysis during playback
- **Advanced ML Models**: Integration with specialized music AI models
- **Social Features**: Collaborative playlist creation and sharing
- **API Endpoints**: REST API for external integrations
- **Mobile App**: Cross-platform mobile application
