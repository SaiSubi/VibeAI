# Debug & Utility Scripts

This folder contains various debug and utility scripts created during the development of VibeAI v2.

## Database Scripts

### `check_db.py`
- Lists all users in the PostgreSQL database
- Shows user ID, name, email, and Spotify registration status

### `check_db_token.py`
- Checks details of Spotify tokens stored in PostgreSQL
- Shows token expiration and scopes for a specific user

## Playlist Scripts

### `list_playlists.py`
- Lists all playlists for the authenticated user
- Shows track count, public/private status, and owner

### `check_all_playlists.py`
- Tests different Spotify API endpoints for listing playlists
- Helps debug playlist visibility issues

### `refresh_and_check.py`
- Forces refresh of Spotify access token
- Lists playlists to check if visibility changes propagated

## Audio Features Debug Scripts

### `test_audio_features.py`
- Tests if Spotify API can retrieve audio features for a given track ID
- Uses user's access token

### `test_audio_features_local.py`
- Tests audio features access using track IDs from local song database
- Helps debug 403 errors with audio features

### `test_audio_features_popular.py`
- Tests audio features with very popular tracks (e.g., "Blinding Lights")
- Also attempts client credentials flow

### `test_spotify_credentials.py`
- Verifies Spotify API client credentials
- Tests basic search functionality and audio features

## Token & Scope Scripts

### `check_token_scopes.py`
- Checks the scopes of the current access token
- Helps debug permission issues

## V2 Development Scripts

### `test_small.py`
- Smaller test script to verify database builder works
- Tests with limited set of playlists

## Usage

Most scripts can be run directly:
```bash
python scripts/script_name.py
```

Some scripts require specific parameters or user IDs. Check the individual script files for usage details.

## Notes

- These scripts were created during debugging of the audio features 403 error
- They helped identify playlist visibility and authentication issues
- The audio features issue remains unresolved but the database building works
- V2 development files are now in the `v2/` folder 