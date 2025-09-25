# VibeAI v2 Frontend

A beautiful, modern web interface for VibeAI v2 that matches the design from the provided image.

## Features

- **Natural Language Search**: Tell the app what you want to listen to in plain English
- **Advanced Filters**: Filter by artist, genre, emotion, energy level, lyrical themes, and release date
- **Default Playlists**: Pre-configured playlists for different moods and occasions
- **Real-time Search**: Instant search results as you type
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Modern dark interface that's easy on the eyes

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   python run.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5001`

## Usage

### Search
- Type your mood or what you want to listen to in the search bar
- Use the mood buttons on the left for quick suggestions
- Combine with filters for more precise results

### Filters
- Click any filter button to open filter options
- Set multiple criteria to narrow down results
- Filters work together with natural language search

### Default Playlists
- Click on any playlist in the sidebar to load pre-configured songs
- Each playlist has specific parameters and natural language queries

## API Endpoints

- `GET /` - Main interface
- `POST /api/search` - Search songs with natural language and filters
- `GET /api/playlists` - Get list of default playlists
- `POST /api/playlist/<id>` - Get songs for a specific playlist

## Design Features

- **Left Sidebar**: Logo, mood buttons, and default playlists
- **Search Bar**: Natural language input with real-time search
- **Filter Buttons**: Quick access to different filter types
- **Popularity Slider**: Adjust popularity range
- **Track List**: Beautiful track display with album art placeholders
- **Modal Filters**: Detailed filter options in popup modals

## Customization

The frontend is designed to be easily customizable:

- **Colors**: Modify the CSS variables in `static/css/styles.css`
- **Playlists**: Add new playlists in `app.py` in the `get_default_playlists()` function
- **Filters**: Add new filter types by extending the modal creation functions
- **Styling**: All styles are in `static/css/styles.css` with clear organization

## Backend Integration

This frontend integrates with the VibeAI v2 backend:
- Uses `SongSearchEngine` for natural language processing
- Uses `SongManager` for database operations
- Combines filters with natural language queries
- Provides a clean API layer for the frontend

## Development

To modify the frontend:

1. Edit HTML templates in `templates/`
2. Update styles in `static/css/styles.css`
3. Modify JavaScript in `static/js/script.js`
4. Update API endpoints in `app.py`

The app runs in debug mode by default, so changes will be reflected immediately.
