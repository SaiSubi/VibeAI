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
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from song_search import SongSearchEngine
from song_manager import SongManager
from simplified_agentic_search import agentic_song_search

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
        
        print(f"🔍 Backend returning {len(results)} songs")
        if results:
            print(f"📋 First song structure: {list(results[0].keys())}")
            print(f"📋 First song sample: {results[0]}")
        
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

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of all languages for filtering"""
    try:
        conn = song_manager.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT language FROM songs WHERE language IS NOT NULL AND language != '' ORDER BY language")
        languages = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'languages': languages
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        },
        {
            'id': 'road_trip',
            'name': 'Road Trip',
            'query': 'upbeat songs perfect for a road trip adventure',
            'filters': {
                'energy_levels': ['medium', 'high'],
                'tempo_levels': ['medium', 'fast'],
                'themes': ['Adventure', 'Feel Good', 'Nostalgia']
            },
            'description': 'Hit the road with these perfect tunes'
        },
        {
            'id': 'coffee_shop',
            'name': 'Coffee Shop Jazz',
            'query': 'smooth jazz and acoustic songs for a coffee shop vibe',
            'filters': {
                'genres': ['Jazz', 'Acoustic', 'Folk'],
                'energy_levels': ['low', 'medium'],
                'tempo_levels': ['slow', 'medium']
            },
            'description': 'Perfect background music for your coffee break'
        },
        {
            'id': 'rainy_day',
            'name': 'Rainy Day',
            'query': 'melancholic and introspective songs for a rainy day',
            'filters': {
                'energy_levels': ['low'],
                'tempo_levels': ['slow'],
                'themes': ['Melancholy', 'Reflection/Introspection', 'Nostalgia']
            },
            'description': 'Cozy up with these rainy day melodies'
        },
        {
            'id': 'focus_flow',
            'name': 'Focus Flow',
            'query': 'instrumental and ambient music for deep focus',
            'filters': {
                'include_instrumentals': True,
                'energy_levels': ['low', 'medium'],
                'tempo_levels': ['slow', 'medium']
            },
            'description': 'Stay focused with these ambient tracks'
        },
        {
            'id': 'sunset_vibes',
            'name': 'Sunset Vibes',
            'query': 'warm and mellow songs perfect for watching the sunset',
            'filters': {
                'energy_levels': ['low', 'medium'],
                'tempo_levels': ['slow', 'medium'],
                'themes': ['Peaceful', 'Reflection/Introspection', 'Warm']
            },
            'description': 'Wind down with these sunset melodies'
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

@app.route('/api/agentic-search', methods=['POST'])
def agentic_search():
    """Agentic AI song search using multi-agent system"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        max_results = data.get('max_results', 10)
        
        if not query.strip():
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        print(f"🎵 Agentic search request: '{query}' (max_results: {max_results}, filters: {filters})")
        
        # Call the agentic search system with filters
        result = agentic_song_search(query, max_results, filters)
        
        print(f"✅ Agentic search completed: {result['total_selected']} songs found using {result['search_method']} method")
        
        # Format songs for frontend
        formatted_songs = []
        for song in result['songs']:
            formatted_song = {
                'id': song.get('id'),
                'title': song.get('title'),
                'artist': song.get('artist'),
                'album': song.get('album', ''),
                'release_year': song.get('release_year', ''),
                'spotify_id': song.get('spotify_id'),
                'spotify_uri': song.get('spotify_uri'),
                'match_score': song.get('match_score', 0),
                'reasoning': song.get('reasoning', ''),
                'energy_level': song.get('energy_level', 0),
                'popularity_score': song.get('popularity_score', 0),
                'genre': song.get('genre', ''),
                'language': song.get('language', ''),
                'mood_tags': song.get('mood_tags', ''),
                'lyrical_themes': song.get('lyrical_themes', ''),
                'tempo': song.get('tempo', 0),
                'danceability_score': song.get('danceability_score', 0),
                'acousticness': song.get('acousticness', 0)
            }
            formatted_songs.append(formatted_song)
        
        return jsonify({
            'success': True,
            'songs': formatted_songs,
            'total': len(formatted_songs),
            'query': query,
            'query_interpretation': result['query_interpretation'],
            'search_method': result['search_method'],
            'total_candidates': result['total_candidates'],
            'total_selected': result['total_selected'],
            'selection_reasoning': result['selection_reasoning'],
            'enriched_query': result['enriched_query'],
            'is_agentic': True
        })
        
    except Exception as e:
        print(f"❌ Error in agentic search: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-spotify-playlist', methods=['POST'])
def create_spotify_playlist():
    """Create a Spotify playlist from search results"""
    try:
        data = request.get_json()
        songs = data.get('songs', [])
        playlist_name = data.get('playlist_name', 'VibeAI Search Results')
        
        if not songs:
            return jsonify({
                'success': False,
                'error': 'No songs provided'
            }), 400
        
        # Extract Spotify URIs from songs
        track_uris = []
        invalid_songs = []
        
        for song in songs:
            if song.get('spotify_uri') and song.get('spotify_uri') != 'spotify:track:':
                track_uris.append(song['spotify_uri'])
            elif song.get('spotify_id'):
                spotify_id = song['spotify_id']
                # Clean and validate Spotify ID
                if spotify_id and isinstance(spotify_id, str):
                    spotify_id = spotify_id.strip()
                    # Validate Spotify ID format (22 characters, alphanumeric)
                    if len(spotify_id) == 22 and spotify_id.isalnum():
                        track_uris.append(f"spotify:track:{spotify_id}")
                    else:
                        invalid_songs.append({
                            'id': spotify_id,
                            'title': song.get('title', 'Unknown'),
                            'artist': song.get('artist', 'Unknown'),
                            'reason': f'Invalid format (length: {len(spotify_id)})'
                        })
                else:
                    invalid_songs.append({
                        'id': spotify_id,
                        'title': song.get('title', 'Unknown'),
                        'artist': song.get('artist', 'Unknown'),
                        'reason': 'Empty or invalid type'
                    })
            else:
                invalid_songs.append({
                    'id': None,
                    'title': song.get('title', 'Unknown'),
                    'artist': song.get('artist', 'Unknown'),
                    'reason': 'No Spotify ID or URI'
                })
        
        print(f"🎵 Creating playlist with {len(track_uris)} valid tracks")
        if invalid_songs:
            print(f"⚠️ Skipped {len(invalid_songs)} invalid songs")
        
        if not track_uris:
            return jsonify({
                'success': False,
                'error': 'No valid Spotify URIs found'
            }), 400
        
        # Import Spotify functions
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".."))
        from utils.spotify import create_playlist, add_tracks_to_playlist
        from utils.token import get_service_account_access_token
        
        # Get service account token for anonymous use
        access_token = get_service_account_access_token()
        if not access_token:
            return jsonify({
                'success': False,
                'error': 'Failed to get Spotify access token'
            }), 500
        
        # Get the actual Spotify user ID for the service account
        import requests
        user_response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Failed to get user info: {user_response.json()}'
            }), 500
        
        service_user_id = user_response.json()['id']
        
        # Create playlist (using service account user ID)
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        unique_playlist_name = f"{playlist_name} - {unique_id}"
        
        playlist = create_playlist(
            user_id=service_user_id,
            access_token=access_token,
            playlist_name=unique_playlist_name,
            description=f"Created by VibeAI - {len(track_uris)} songs",
            public=True
        )
        
        if 'error' in playlist:
            return jsonify({
                'success': False,
                'error': f"Failed to create playlist: {playlist['error']}"
            }), 500
        
        playlist_id = playlist["id"]
        playlist_url = playlist["external_urls"]["spotify"]
        
        # Add tracks to playlist with retry logic
        print(f"🎵 Adding {len(track_uris)} tracks to playlist")
        
        add_response = add_tracks_to_playlist(playlist_id, track_uris, access_token)
        
        if 'error' in add_response:
            error_details = add_response['error']
            if isinstance(error_details, dict) and 'message' in error_details:
                error_message = f"Spotify API error: {error_details}"
            else:
                error_message = f"Failed to add tracks: {error_details}"
            
            print(f"❌ Error adding tracks: {error_message}")
            
            # If we have many tracks, try with fewer tracks to isolate the problematic ones
            if len(track_uris) > 5:
                print(f"🔄 Retrying with first 5 tracks only...")
                retry_response = add_tracks_to_playlist(playlist_id, track_uris[:5], access_token)
                if 'error' not in retry_response:
                    print(f"✅ Successfully added {len(track_uris[:5])} tracks (out of {len(track_uris)} requested)")
                    return jsonify({
                        'success': True,
                        'playlist_id': playlist_id,
                        'playlist_url': playlist_url,
                        'playlist_name': unique_playlist_name,
                        'tracks_added': len(track_uris[:5]),
                        'warning': f'Only {len(track_uris[:5])} tracks added due to API errors'
                    })
            
            return jsonify({
                'success': False,
                'error': error_message
            }), 500
        
        return jsonify({
            'success': True,
            'playlist_id': playlist_id,
            'playlist_url': playlist_url,
            'playlist_name': unique_playlist_name,
            'tracks_added': len(track_uris)
        })
        
    except Exception as e:
        print(f"❌ Error creating Spotify playlist: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
