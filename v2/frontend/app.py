#!/usr/bin/env python3
"""
VibeAI v2 - Web Frontend API
Flask API for the VibeAI v2 web interface
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from song_search import SongSearchEngine
from song_manager import SongManager

app = Flask(__name__)
CORS(app)

# Initialize search engines
search_engine = SongSearchEngine()
song_manager = SongManager()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_songs():
    """Search songs with natural language and filters"""
    try:
        data = request.get_json()
        
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
            # Don't convert artists to string - pass them directly to SongSearchEngine
            songs = search_with_gemini_and_filters(query, converted_filters, popularity_min, popularity_max, limit)
        else:
            # Use manual filtering without Gemini
            songs = search_with_manual_filters(converted_filters, popularity_min, popularity_max, limit)
        
        # Apply additional filters if needed
        filtered_songs = apply_additional_filters(songs, converted_filters)
        
        # Limit results
        results = filtered_songs[:limit]
        
        return jsonify({
            'success': True,
            'songs': results,
            'total': len(results),
            'query': query,
            'used_gemini': use_gemini and bool(query)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

@app.route('/api/artists', methods=['GET'])
def get_artists():
    """Get list of all artists for autocomplete"""
    try:
        conn = song_manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT artist FROM songs WHERE artist IS NOT NULL ORDER BY artist")
        artists = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'artists': artists
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/playlists', methods=['GET'])
def get_default_playlists():
    """Get default playlists with predefined parameters"""
    playlists = [
        {
            'id': 'late_night_drive',
            'name': 'Late Night Drive',
            'query': 'moody atmospheric songs for driving at night',
            'filters': {
                'energy_levels': ['low', 'medium'],
                'tempo_levels': ['slow', 'medium'],
                'themes': ['Nostalgia', 'Reflection/Introspection']
            },
            'description': 'Perfect for those late night drives'
        },
        {
            'id': 'workout_energy',
            'name': 'Workout Energy',
            'query': 'high energy motivational songs for working out',
            'filters': {
                'energy_levels': ['high'],
                'tempo_levels': ['fast'],
                'themes': ['Motivational', 'Feel Good']
            },
            'description': 'Get pumped up for your workout'
        },
        {
            'id': 'romantic_evening',
            'name': 'Romantic Evening',
            'query': 'romantic love songs for a cozy evening',
            'filters': {
                'energy_levels': ['low', 'medium'],
                'tempo_levels': ['slow', 'medium'],
                'themes': ['In Love', 'Hopeful Love', 'Romantic']
            },
            'description': 'Perfect for a romantic evening'
        },
        {
            'id': 'party_time',
            'name': 'Party Time',
            'query': 'danceable party songs to get everyone moving',
            'filters': {
                'energy_levels': ['high'],
                'danceability_levels': ['high'],
                'themes': ['Celebrating Life', 'Feel Good', 'Carefree']
            },
            'description': 'Get the party started!'
        },
        {
            'id': 'chill_vibes',
            'name': 'Chill Vibes',
            'query': 'relaxing chill songs for unwinding',
            'filters': {
                'energy_levels': ['low'],
                'tempo_levels': ['slow'],
                'themes': ['Feel Good', 'Carefree', 'Solitude']
            },
            'description': 'Perfect for relaxing and unwinding'
        }
    ]
    
    return jsonify({
        'success': True,
        'playlists': playlists
    })

@app.route('/api/playlist/<playlist_id>', methods=['POST'])
def get_playlist_songs(playlist_id):
    """Get songs for a specific playlist"""
    try:
        # Get playlist definition
        playlists_response = get_default_playlists()
        playlists = playlists_response.get_json()['playlists']
        
        playlist = next((p for p in playlists if p['id'] == playlist_id), None)
        if not playlist:
            return jsonify({'success': False, 'error': 'Playlist not found'}), 404
        
        # Search for songs using playlist parameters
        query = playlist['query']
        filters = playlist['filters']
        
        # Convert filter levels to numeric ranges
        converted_filters = convert_filter_levels_to_ranges(filters)
        
        # Build combined query
        combined_query = build_combined_query(query, converted_filters, 0, 10)
        
        # Search songs
        songs = search_engine.search_with_natural_language(combined_query)
        
        return jsonify({
            'success': True,
            'playlist': playlist,
            'songs': songs[:20]  # Limit to 20 songs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    
    return converted

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
    
    # Note: We don't add artists here anymore - they're handled separately
    
    if filters.get('languages'):
        languages = filters['languages']
        if languages:
            query_parts.append(f"{', '.join(languages)} songs")
    
    # Add popularity filter
    if popularity_min > 0 or popularity_max < 10:
        query_parts.append(f"popularity between {popularity_min} and {popularity_max}")
    
    return " ".join(query_parts)

def search_with_manual_filters(filters, popularity_min, popularity_max, limit):
    """Search songs using only manual filters without Gemini"""
    try:
        conn = song_manager.get_db_connection()
        cursor = conn.cursor()
        
        # Build SQL query
        where_conditions = []
        params = []
        
        # Energy filter
        if filters.get('energy_range'):
            energy_min, energy_max = filters['energy_range']
            where_conditions.append("energy_level BETWEEN ? AND ?")
            params.extend([energy_min, energy_max])
        
        # Tempo filter
        if filters.get('tempo_range'):
            tempo_min, tempo_max = filters['tempo_range']
            where_conditions.append("tempo BETWEEN ? AND ?")
            params.extend([tempo_min, tempo_max])
        
        # Danceability filter
        if filters.get('danceability_range'):
            dance_min, dance_max = filters['danceability_range']
            where_conditions.append("danceability_score BETWEEN ? AND ?")
            params.extend([dance_min, dance_max])
        
        # Popularity filter
        if popularity_min > 0 or popularity_max < 10:
            where_conditions.append("popularity_score BETWEEN ? AND ?")
            params.extend([popularity_min, popularity_max])
        
        # Year range filter
        if filters.get('year_range'):
            year_min, year_max = filters['year_range']
            where_conditions.append("release_year BETWEEN ? AND ?")
            params.extend([year_min, year_max])
        
        # Artist filter - case insensitive partial matching
        if filters.get('artists'):
            artist_conditions = []
            for artist in filters['artists']:
                artist_conditions.append("LOWER(artist) LIKE ?")
                params.append(f"%{artist.lower()}%")
            where_conditions.append(f"({' OR '.join(artist_conditions)})")
        
        # Genre filter - case insensitive partial matching
        if filters.get('genres'):
            genre_conditions = []
            for genre in filters['genres']:
                genre_conditions.append("LOWER(genre) LIKE ?")
                params.append(f"%{genre.lower()}%")
            where_conditions.append(f"({' OR '.join(genre_conditions)})")
        
        # Theme filter - case insensitive partial matching
        if filters.get('themes'):
            theme_conditions = []
            for theme in filters['themes']:
                theme_conditions.append("LOWER(lyrical_themes) LIKE ?")
                params.append(f"%{theme.lower()}%")
            where_conditions.append(f"({' OR '.join(theme_conditions)})")
        
        # Language filter - case insensitive partial matching
        if filters.get('languages'):
            language_conditions = []
            for language in filters['languages']:
                language_conditions.append("LOWER(language) LIKE ?")
                params.append(f"%{language.lower()}%")
            where_conditions.append(f"({' OR '.join(language_conditions)})")
        
        # Build final query
        query = "SELECT * FROM songs"
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        query += " ORDER BY popularity_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        songs = []
        
        for row in cursor.fetchall():
            song = dict(zip(columns, row))
            songs.append(song)
        
        conn.close()
        return songs
        
    except Exception as e:
        print(f"Error in manual search: {e}")
        return []

def apply_additional_filters(songs, filters):
    """Apply additional filters to search results"""
    # Since we now handle all filtering in the SQL query,
    # this function is mainly for any post-processing if needed
    return songs

if __name__ == '__main__':
    app.run(debug=True, port=5001)
