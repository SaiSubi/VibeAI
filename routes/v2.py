#!/usr/bin/env python3
"""
VibeAI v2 - FastAPI Router
FastAPI router for VibeAI v2 agentic search functionality
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from v2.simplified_agentic_search import agentic_song_search
from v2.song_manager import SongManager
from v2.song_search import SongSearchEngine

router = APIRouter(prefix="/v2", tags=["v2"])

# Initialize search engines
song_manager = SongManager()
search_engine = SongSearchEngine()

# Setup templates
templates = Jinja2Templates(directory="v2/templates")

# Default playlists for v2
DEFAULT_PLAYLISTS = {
    "late_night_drive": {
        "name": "Late Night Drive",
        "description": "Moody atmospheric songs for driving at night",
        "query": "moody atmospheric songs for driving at night",
        "filters": {"energy_range": [3, 7], "themes": ["Nostalgia", "Reflection/Introspection"]}
    },
    "workout_energy": {
        "name": "Workout Energy", 
        "description": "High energy motivational songs for workouts",
        "query": "high energy motivational workout songs",
        "filters": {"energy_range": [7, 10], "themes": ["Motivational", "Feel Good"]}
    },
    "romantic_evening": {
        "name": "Romantic Evening",
        "description": "Romantic love songs for a special evening",
        "query": "romantic love songs for a special evening",
        "filters": {"energy_range": [3, 6], "themes": ["In Love", "Hopeful Love"]}
    },
    "party_time": {
        "name": "Party Time",
        "description": "Danceable party songs to get everyone moving",
        "query": "danceable party songs to get everyone moving",
        "filters": {"energy_range": [6, 10], "danceability_range": [7, 10]}
    },
    "chill_vibes": {
        "name": "Chill Vibes",
        "description": "Relaxing chill songs for unwinding",
        "query": "relaxing chill songs for unwinding",
        "filters": {"energy_range": [1, 4], "themes": ["Carefree", "Solitude"]}
    }
}

def convert_filter_levels_to_ranges(filters):
    """Convert filter levels (low/medium/high) to numeric ranges"""
    converted = filters.copy()
    
    # Convert energy levels
    if 'energy_levels' in converted:
        energy_ranges = []
        for level in converted['energy_levels']:
            if level == 'low':
                energy_ranges.extend([1, 2, 3])
            elif level == 'medium':
                energy_ranges.extend([4, 5, 6])
            elif level == 'high':
                energy_ranges.extend([7, 8, 9, 10])
        
        if energy_ranges:
            converted['energy_range'] = [min(energy_ranges), max(energy_ranges)]
        del converted['energy_levels']
    
    # Convert tempo levels
    if 'tempo_levels' in converted:
        tempo_ranges = []
        for level in converted['tempo_levels']:
            if level == 'slow':
                tempo_ranges.extend([1, 2, 3])
            elif level == 'medium':
                tempo_ranges.extend([4, 5, 6])
            elif level == 'fast':
                tempo_ranges.extend([7, 8, 9, 10])
        
        if tempo_ranges:
            converted['tempo_range'] = [min(tempo_ranges), max(tempo_ranges)]
        del converted['tempo_levels']
    
    # Convert danceability levels
    if 'danceability_levels' in converted:
        danceability_ranges = []
        for level in converted['danceability_levels']:
            if level == 'low':
                danceability_ranges.extend([1, 2, 3])
            elif level == 'medium':
                danceability_ranges.extend([4, 5, 6])
            elif level == 'high':
                danceability_ranges.extend([7, 8, 9, 10])
        
        if danceability_ranges:
            converted['danceability_range'] = [min(danceability_ranges), max(danceability_ranges)]
        del converted['danceability_levels']
    
    # Handle new filter types
    if 'genre' in converted:
        converted['genres'] = [converted['genre']]
        del converted['genre']
    
    if 'decade' in converted:
        decade = converted['decade']
        if decade:
            # Convert decade to year range
            decade_year = int(decade.replace('s', ''))
            converted['year_range'] = [decade_year, decade_year + 9]
        del converted['decade']
    
    return converted

def search_with_gemini_and_filters(query, filters, popularity_min, popularity_max, limit):
    """Search using Gemini with proper filter handling"""
    try:
        # First, get the natural language search results
        combined_query = build_combined_query(query, {}, popularity_min, popularity_max)
        songs = search_engine.search_with_natural_language(combined_query)
        
        # Then apply artist/genre/theme filters manually
        if filters.get('artists'):
            artist_names = [name.lower() for name in filters['artists']]
            songs = [song for song in songs if any(artist in song.get('artist', '').lower() for artist in artist_names)]
        
        if filters.get('genres'):
            genre_names = [genre.lower() for genre in filters['genres']]
            songs = [song for song in songs if any(genre in song.get('genre', '').lower() for genre in genre_names)]
        
        if filters.get('themes'):
            theme_names = [theme.lower() for theme in filters['themes']]
            songs = [song for song in songs if any(theme in song.get('lyrical_themes', '').lower() for theme in theme_names)]
        
        if filters.get('languages'):
            language_names = [lang.lower() for lang in filters['languages']]
            songs = [song for song in songs if any(lang in song.get('language', '').lower() for lang in language_names)]
        
        return songs
        
    except Exception as e:
        print(f"Error in Gemini search: {e}")
        return []

def build_combined_query(natural_query, filters, popularity_min, popularity_max):
    """Build a combined query from natural language and filters"""
    query_parts = []
    
    # Add natural language query
    if natural_query:
        query_parts.append(natural_query)
    
    # Add filter-based queries (only for non-text filters)
    if filters.get('energy_range'):
        energy_min, energy_max = filters['energy_range']
        if energy_min > 0 or energy_max < 10:
            query_parts.append(f"energy level between {energy_min} and {energy_max}")
    
    if filters.get('tempo_range'):
        tempo_min, tempo_max = filters['tempo_range']
        if tempo_min > 0 or tempo_max < 10:
            query_parts.append(f"tempo between {tempo_min} and {tempo_max}")
    
    if filters.get('danceability_range'):
        dance_min, dance_max = filters['danceability_range']
        if dance_min > 0 or dance_max < 10:
            query_parts.append(f"danceable songs between {dance_min} and {dance_max}")
    
    if filters.get('themes'):
        themes = filters['themes']
        if themes:
            query_parts.append(f"songs with themes: {', '.join(themes)}")
    
    if filters.get('genres'):
        genres = filters['genres']
        if genres:
            query_parts.append(f"{', '.join(genres)} songs")
    
    if filters.get('languages'):
        languages = filters['languages']
        if languages:
            query_parts.append(f"{', '.join(languages)} songs")
    
    # Add popularity filter
    if popularity_min > 0 or popularity_max < 10:
        query_parts.append(f"popularity between {popularity_min} and {popularity_max}")
    
    return " ".join(query_parts)

@router.get("/", response_class=HTMLResponse)
async def v2_home(request: Request):
    """Serve the VibeAI v2 frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/api/search")
async def search_songs(request: Request):
    """Search songs with natural language and filters"""
    try:
        if not AGENTIC_SEARCH_AVAILABLE:
            return JSONResponse({
                'success': False,
                'error': 'Search temporarily unavailable - dependencies loading'
            }, status_code=503)
            
        data = await request.json()
        
        # Extract search parameters
        query = data.get('query', '')
        filters = data.get('filters', {})
        popularity_min = data.get('popularity_min', 0)
        popularity_max = data.get('popularity_max', 10)
        limit = data.get('limit', 20)
        use_gemini = data.get('use_gemini', True)
        
        # Convert filter levels to numeric ranges
        converted_filters = convert_filter_levels_to_ranges(filters)
        
        if use_gemini and query:
            # Use Gemini for natural language processing
            songs = search_with_gemini_and_filters(query, converted_filters, popularity_min, popularity_max, limit)
        else:
            # Use manual filtering without Gemini
            songs = search_engine.search_songs(converted_filters)
        
        # Limit results
        results = songs[:limit]
        
        print(f"🔍 Backend returning {len(results)} songs")
        
        return JSONResponse({
            'success': True,
            'songs': results,
            'total': len(results),
            'query': query,
            'used_gemini': use_gemini and bool(query)
        })
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)

@router.post("/api/agentic-search")
async def agentic_search(request: Request):
    """Agentic AI song search using multi-agent system"""
    try:
        data = await request.json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        max_results = data.get('max_results', 10)
        
        if not query.strip():
            return JSONResponse({
                'success': False,
                'error': 'Query cannot be empty'
            }, status_code=400)
        
        print(f"🎵 Agentic search request: '{query}' (max_results: {max_results}, filters: {filters})")
        
        # Call the agentic search system with filters
        result = agentic_song_search(query, max_results, filters)
        
        print(f"✅ Agentic search completed: {result['total_selected']} songs found using {result['search_method']} method")
        
        # Format songs for frontend
        formatted_songs = []
        for song in result['songs']:
            formatted_song = {
                'id': song.get('id'),
                'spotify_id': song.get('spotify_id'),
                'title': song.get('title'),
                'artist': song.get('artist'),
                'album': song.get('album'),
                'release_year': song.get('release_year'),
                'duration_ms': song.get('duration_ms'),
                'popularity': song.get('popularity'),
                'energy_level': song.get('energy_level'),
                'popularity_score': song.get('popularity_score'),
                'genre': song.get('genre'),
                'language': song.get('language'),
                'lyrical_themes': song.get('lyrical_themes'),
                'song_description': song.get('song_description'),
                'spotify_uri': song.get('spotify_uri'),
                'match_score': song.get('match_score'),
                'reasoning': song.get('reasoning')
            }
            formatted_songs.append(formatted_song)
        
        return JSONResponse({
            'success': True,
            'songs': formatted_songs,
            'total': result['total_selected'],
            'query': query,
            'search_method': result['search_method'],
            'total_candidates': result.get('total_candidates', 0),
            'total_unique': result.get('total_unique', 0)
        })
        
    except Exception as e:
        print(f"❌ Agentic search error: {e}")
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)

@router.get("/api/playlists")
async def get_playlists():
    """Get list of default playlists"""
    return JSONResponse({
        'success': True,
        'playlists': DEFAULT_PLAYLISTS
    })

@router.post("/api/playlist/{playlist_id}")
async def load_playlist(playlist_id: str, request: Request):
    """Load songs for a specific playlist"""
    try:
        if playlist_id not in DEFAULT_PLAYLISTS:
            return JSONResponse({
                'success': False,
                'error': 'Playlist not found'
            }, status_code=404)
        
        playlist = DEFAULT_PLAYLISTS[playlist_id]
        
        # Use agentic search to get playlist songs
        result = agentic_song_search(
            playlist['query'], 
            max_results=20, 
            user_filters=playlist.get('filters', {})
        )
        
        # Format songs for frontend
        formatted_songs = []
        for song in result['songs']:
            formatted_song = {
                'id': song.get('id'),
                'spotify_id': song.get('spotify_id'),
                'title': song.get('title'),
                'artist': song.get('artist'),
                'album': song.get('album'),
                'release_year': song.get('release_year'),
                'duration_ms': song.get('duration_ms'),
                'popularity': song.get('popularity'),
                'energy_level': song.get('energy_level'),
                'popularity_score': song.get('popularity_score'),
                'genre': song.get('genre'),
                'language': song.get('language'),
                'lyrical_themes': song.get('lyrical_themes'),
                'song_description': song.get('song_description'),
                'spotify_uri': song.get('spotify_uri'),
                'match_score': song.get('match_score'),
                'reasoning': song.get('reasoning')
            }
            formatted_songs.append(formatted_song)
        
        return JSONResponse({
            'success': True,
            'playlist': playlist,
            'songs': formatted_songs,
            'total': len(formatted_songs)
        })
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)

@router.get("/api/languages")
async def get_languages():
    """Get list of all languages for filtering"""
    try:
        conn = song_manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT language FROM songs WHERE language IS NOT NULL AND language != '' ORDER BY language")
        languages = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return JSONResponse({
            'success': True,
            'languages': languages
        })
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)

@router.get("/api/artists")
async def get_artists():
    """Get list of all artists for filtering"""
    try:
        conn = song_manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT artist FROM songs WHERE artist IS NOT NULL AND artist != '' ORDER BY artist")
        artists = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return JSONResponse({
            'success': True,
            'artists': artists
        })
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)
