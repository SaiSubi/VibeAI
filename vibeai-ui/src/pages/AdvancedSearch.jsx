import React, { useState, useEffect } from 'react';
import { agenticSearch, getDefaultPlaylists, getAvailableArtists, getAvailableLanguages } from '../api';
import { useNavigate } from 'react-router-dom';

function AdvancedSearch() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [results, setResults] = useState([]);
  const [playlists, setPlaylists] = useState({});
  const [artists, setArtists] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [playlistsData, artistsData, languagesData] = await Promise.all([
      getDefaultPlaylists(),
      getAvailableArtists(),
      getAvailableLanguages()
    ]);
    
    if (playlistsData.success) setPlaylists(playlistsData.playlists);
    if (artistsData.success) setArtists(artistsData.artists);
    if (languagesData.success) setLanguages(languagesData.languages);
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await agenticSearch(query, filters, 10);
      if (response.success) {
        setResults(response.songs);
      } else {
        console.error('Search failed:', response.error);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlaylistClick = (playlist) => {
    setQuery(playlist.query);
    setFilters(playlist.filters);
  };

  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  return (
    <div style={{
      backgroundColor: "#121212",
      color: "white",
      fontFamily: "sans-serif",
      minHeight: "100vh",
      padding: "20px"
    }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", marginBottom: "30px" }}>
        <img src="/logo.png" alt="VibeAI Logo" style={{ width: "60px", marginRight: "15px" }} />
        <div>
          <h1 style={{ margin: 0, fontSize: "2rem" }}>VibeAI v2</h1>
          <p style={{ margin: 0, color: "#ccc" }}>Advanced Music Discovery</p>
        </div>
        <button
          onClick={() => navigate('/')}
          style={{
            marginLeft: "auto",
            padding: "8px 16px",
            backgroundColor: "#1DB954",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          Back to Simple Search
        </button>
      </div>

      {/* Search Section */}
      <div style={{ marginBottom: "30px" }}>
        <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe what you want to listen to... (e.g., 'happy upbeat songs for workout')"
            style={{
              flex: 1,
              padding: "15px",
              fontSize: "16px",
              borderRadius: "8px",
              border: "2px solid #ccc",
              backgroundColor: "white",
              color: "black"
            }}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={() => setShowFilters(!showFilters)}
            style={{
              padding: "15px 20px",
              backgroundColor: showFilters ? "#1DB954" : "#333",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "16px"
            }}
          >
            {showFilters ? "Hide Filters" : "Show Filters"}
          </button>
          <button
            onClick={handleSearch}
            disabled={!query.trim() || isLoading}
            style={{
              padding: "15px 30px",
              backgroundColor: isLoading ? "#888" : "#1DB954",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: isLoading ? "not-allowed" : "pointer",
              fontSize: "16px",
              fontWeight: "bold"
            }}
          >
            {isLoading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div style={{
            backgroundColor: "#1a1a1a",
            padding: "20px",
            borderRadius: "8px",
            marginBottom: "20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
              <h3 style={{ margin: 0 }}>Advanced Filters</h3>
              <button
                onClick={clearFilters}
                style={{
                  padding: "5px 10px",
                  backgroundColor: "#666",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer"
                }}
              >
                Clear All
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
              {/* Artist Filter */}
              <div>
                <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Artist</label>
                <select
                  value={filters.artists || ''}
                  onChange={(e) => updateFilter('artists', e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "4px",
                    backgroundColor: "white",
                    color: "black"
                  }}
                >
                  <option value="">Any Artist</option>
                  {artists.slice(0, 20).map(artist => (
                    <option key={artist} value={artist}>{artist}</option>
                  ))}
                </select>
              </div>

              {/* Language Filter */}
              <div>
                <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Language</label>
                <select
                  value={filters.language || ''}
                  onChange={(e) => updateFilter('language', e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "4px",
                    backgroundColor: "white",
                    color: "black"
                  }}
                >
                  <option value="">Any Language</option>
                  {languages.map(lang => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
              </div>

              {/* Energy Level */}
              <div>
                <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Energy Level</label>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={filters.energy_level || 5}
                    onChange={(e) => updateFilter('energy_level', parseInt(e.target.value))}
                    style={{ flex: 1 }}
                  />
                  <span style={{ minWidth: "20px" }}>{filters.energy_level || 5}</span>
                </div>
              </div>

              {/* Popularity */}
              <div>
                <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Popularity</label>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={filters.popularity_score || 5}
                    onChange={(e) => updateFilter('popularity_score', parseInt(e.target.value))}
                    style={{ flex: 1 }}
                  />
                  <span style={{ minWidth: "20px" }}>{filters.popularity_score || 5}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Default Playlists */}
      <div style={{ marginBottom: "30px" }}>
        <h3 style={{ marginBottom: "15px" }}>Quick Playlists</h3>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
          {Object.entries(playlists).map(([key, playlist]) => (
            <button
              key={key}
              onClick={() => handlePlaylistClick(playlist)}
              style={{
                padding: "12px 20px",
                backgroundColor: "#1DB954",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "bold",
                transition: "background-color 0.2s"
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = "#1ed760"}
              onMouseOut={(e) => e.target.style.backgroundColor = "#1DB954"}
            >
              {playlist.name}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div style={{ textAlign: "center", margin: "40px 0" }}>
          <h3 style={{ marginBottom: "20px" }}>Searching for perfect songs...</h3>
          <img
            src="/loading.gif"
            alt="Loading"
            style={{
              width: "100px",
              height: "100px",
              display: "block",
              margin: "0 auto"
            }}
          />
        </div>
      )}

      {/* Results */}
      {results.length > 0 && !isLoading && (
        <div>
          <h3 style={{ marginBottom: "20px" }}>Search Results ({results.length} songs)</h3>
          <div style={{ display: "grid", gap: "15px" }}>
            {results.map((song, index) => (
              <div
                key={song.id}
                style={{
                  backgroundColor: "#1a1a1a",
                  padding: "20px",
                  borderRadius: "8px",
                  border: "1px solid #333",
                  display: "flex",
                  alignItems: "center",
                  gap: "20px"
                }}
              >
                <div style={{
                  width: "60px",
                  height: "60px",
                  backgroundColor: "#333",
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "24px"
                }}>
                  🎵
                </div>
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: "0 0 5px 0", fontSize: "18px" }}>{song.title}</h4>
                  <p style={{ margin: "0 0 5px 0", color: "#ccc" }}>{song.artist}</p>
                  <p style={{ margin: "0", fontSize: "14px", color: "#888" }}>
                    {song.genre} • {song.language} • Energy: {song.energy_level}/10
                  </p>
                  {song.song_description && (
                    <p style={{ margin: "5px 0 0 0", fontSize: "12px", color: "#aaa", fontStyle: "italic" }}>
                      {song.song_description}
                    </p>
                  )}
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "12px", color: "#888", marginBottom: "5px" }}>
                    #{index + 1}
                  </div>
                  <button
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#1DB954",
                      color: "white",
                      border: "none",
                      borderRadius: "5px",
                      cursor: "pointer",
                      fontSize: "14px"
                    }}
                    onClick={() => {
                      // You can add Spotify play functionality here
                      console.log('Play song:', song.title);
                    }}
                  >
                    Play
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {results.length === 0 && !isLoading && query && (
        <div style={{ textAlign: "center", margin: "40px 0" }}>
          <h3 style={{ color: "#888" }}>No songs found</h3>
          <p style={{ color: "#666" }}>Try adjusting your search or filters</p>
        </div>
      )}

      {/* Footer */}
      <footer style={{ marginTop: "50px", textAlign: "center", fontSize: "12px", color: "#ccc" }}>
        Made by Sai Subramanian. VibeAI v2 with Advanced Search 🎵
      </footer>
    </div>
  );
}

export default AdvancedSearch;
