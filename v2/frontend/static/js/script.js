// VibeAI v2 - Frontend JavaScript

class VibeAIApp {
    constructor() {
        this.currentFilters = {};
        this.currentPlaylist = null;
        this.currentSongs = [];
        this.isPlaying = false;
        this.currentTrackIndex = -1;
        this.lastNaturalQuery = '';
        this.availableArtists = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadDefaultPlaylists();
        this.loadAvailableArtists();
        this.setupSearch();
    }
    
    bindEvents() {
        // Search input
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
        
        // Mood buttons
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.currentTarget.dataset.query;
                searchInput.value = query;
                this.lastNaturalQuery = query;
                this.performSearch();
            });
        });
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.openFilterModal(e.currentTarget.dataset.filter);
            });
        });
        
        // Popularity slider
        const popularitySlider = document.getElementById('popularitySlider');
        popularitySlider.addEventListener('input', () => {
            this.updatePopularityFilter();
        });
        
        // Play all button
        document.getElementById('playAllBtn').addEventListener('click', () => {
            this.playAll();
        });
        
        // Modal events
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeModal();
        });
        
        document.getElementById('applyFilter').addEventListener('click', () => {
            this.applyFilter();
        });
        
        document.getElementById('clearFilter').addEventListener('click', () => {
            this.clearCurrentFilter();
        });
        
        // Clear all filters button
        document.getElementById('clearAllFilters').addEventListener('click', () => {
            this.clearAllFilters();
        });
        
        // Close modal on outside click
        document.getElementById('filterModal').addEventListener('click', (e) => {
            if (e.target.id === 'filterModal') {
                this.closeModal();
            }
        });
    }
    
    async loadAvailableArtists() {
        try {
            const response = await fetch('/api/artists');
            const data = await response.json();
            if (data.success) {
                this.availableArtists = data.artists;
            }
        } catch (error) {
            console.error('Error loading artists:', error);
        }
    }
    
    async loadDefaultPlaylists() {
        try {
            const response = await fetch('/api/playlists');
            const data = await response.json();
            
            if (data.success) {
                this.renderDefaultPlaylists(data.playlists);
            }
        } catch (error) {
            console.error('Error loading playlists:', error);
        }
    }
    
    renderDefaultPlaylists(playlists) {
        const container = document.getElementById('playlistButtons');
        container.innerHTML = '';
        
        playlists.forEach(playlist => {
            const btn = document.createElement('button');
            btn.className = 'playlist-btn';
            btn.innerHTML = `
                <div style="font-weight: 600; margin-bottom: 4px;">${playlist.name}</div>
                <div style="font-size: 11px; color: #888;">${playlist.description}</div>
            `;
            btn.addEventListener('click', () => {
                this.loadPlaylist(playlist.id);
            });
            container.appendChild(btn);
        });
    }
    
    async loadPlaylist(playlistId) {
        try {
            this.showLoading();
            
            const response = await fetch(`/api/playlist/${playlistId}`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.currentPlaylist = data.playlist;
                this.currentSongs = data.songs;
                this.renderSongs(data.songs);
                this.updatePlaylistTitle(data.playlist.name);
            } else {
                this.showError('Failed to load playlist');
            }
        } catch (error) {
            console.error('Error loading playlist:', error);
            this.showError('Error loading playlist');
        }
    }
    
    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        
        try {
            this.showLoading();
            
            // Check if natural language query changed
            const naturalQueryChanged = query !== this.lastNaturalQuery;
            this.lastNaturalQuery = query;
            
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    filters: this.currentFilters,
                    popularity_min: 0,
                    popularity_max: 10,
                    limit: 50,
                    use_gemini: naturalQueryChanged
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSongs = data.songs;
                this.renderSongs(data.songs);
                this.updatePlaylistTitle('Search Results');
            } else {
                this.showError('Search failed');
            }
        } catch (error) {
            console.error('Error performing search:', error);
            this.showError('Search failed');
        }
    }
    
    renderSongs(songs) {
        const container = document.getElementById('tracksList');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const noResults = document.getElementById('noResults');
        
        loadingIndicator.style.display = 'none';
        
        if (!songs || songs.length === 0) {
            noResults.style.display = 'flex';
            container.innerHTML = '';
            return;
        }
        
        noResults.style.display = 'none';
        
        container.innerHTML = songs.map((song, index) => `
            <div class="track-item" data-index="${index}">
                <div class="track-album-art">
                    <i class="fas fa-music"></i>
                </div>
                <div class="track-info">
                    <div class="track-title">${song.title}</div>
                    <div class="track-artist">${song.artist}</div>
                    <div class="track-album">${song.album || 'Unknown Album'}</div>
                </div>
                <div class="track-meta">
                    <div class="track-duration">${this.formatDuration(song.duration_ms || 0)}</div>
                    <i class="fas fa-heart track-heart"></i>
                </div>
            </div>
        `).join('');
        
        // Add click events to tracks
        container.querySelectorAll('.track-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.playTrack(index);
            });
        });
        
        // Add heart click events
        container.querySelectorAll('.track-heart').forEach(heart => {
            heart.addEventListener('click', (e) => {
                e.stopPropagation();
                heart.classList.toggle('liked');
            });
        });
    }
    
    playTrack(index) {
        // Remove playing class from all tracks
        document.querySelectorAll('.track-item').forEach(item => {
            item.classList.remove('playing');
        });
        
        // Add playing class to current track
        const trackItem = document.querySelector(`[data-index="${index}"]`);
        if (trackItem) {
            trackItem.classList.add('playing');
        }
        
        this.currentTrackIndex = index;
        this.isPlaying = true;
        
        // Here you would integrate with your audio player
        console.log('Playing:', this.currentSongs[index]);
    }
    
    playAll() {
        if (this.currentSongs.length > 0) {
            this.playTrack(0);
        }
    }
    
    openFilterModal(filterType) {
        const modal = document.getElementById('filterModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Filter by ${filterType.replace('_', ' ').toUpperCase()}`;
        
        // Create filter content based on type
        let content = '';
        switch (filterType) {
            case 'artist':
                content = this.createArtistFilter();
                break;
            case 'genre':
                content = this.createGenreFilter();
                break;
            case 'emotion':
                content = this.createEmotionFilter();
                break;
            case 'energy':
                content = this.createEnergyFilter();
                break;
            case 'tempo':
                content = this.createTempoFilter();
                break;
            case 'danceability':
                content = this.createDanceabilityFilter();
                break;
            case 'lyrical_theme':
                content = this.createLyricalThemeFilter();
                break;
            case 'release_date':
                content = this.createReleaseDateFilter();
                break;
        }
        
        modalBody.innerHTML = content;
        modal.style.display = 'block';
        
        // Store current filter type
        this.currentFilterType = filterType;
        
        // Set up autocomplete for artist filter
        if (filterType === 'artist') {
            this.setupArtistAutocomplete();
        }
    }
    
    createArtistFilter() {
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Artists</label>
                    <div class="autocomplete-container">
                        <input type="text" id="artistSearchInput" placeholder="Type artist name..." autocomplete="off">
                        <div class="autocomplete-dropdown" id="artistDropdown"></div>
                    </div>
                    <div class="selected-items" id="selectedArtists"></div>
                </div>
            </div>
        `;
    }
    
    createGenreFilter() {
        const genres = ['Pop', 'Rock', 'Hip-Hop', 'R&B', 'Electronic', 'Country', 'Jazz', 'Classical', 'Folk', 'Indie', 'Bollywood', 'Tamil Film'];
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Genres</label>
                    <div class="checkbox-group">
                        ${genres.map(genre => `
                            <div class="checkbox-item">
                                <input type="checkbox" id="genre_${genre.replace(/[^a-zA-Z0-9]/g, '_')}" value="${genre}">
                                <label for="genre_${genre.replace(/[^a-zA-Z0-9]/g, '_')}">${genre}</label>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    createEmotionFilter() {
        const emotions = ['Happy', 'Sad', 'Angry', 'Neutral'];
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Emotions</label>
                    <div class="checkbox-group">
                        ${emotions.map(emotion => `
                            <div class="checkbox-item">
                                <input type="checkbox" id="emotion_${emotion}" value="${emotion}">
                                <label for="emotion_${emotion}">${emotion}</label>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    createEnergyFilter() {
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Energy Levels</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="energy_low" value="low">
                            <label for="energy_low">Low Energy (1-3)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="energy_medium" value="medium">
                            <label for="energy_medium">Medium Energy (4-6)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="energy_high" value="high">
                            <label for="energy_high">High Energy (7-10)</label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    createTempoFilter() {
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Tempo</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="tempo_slow" value="slow">
                            <label for="tempo_slow">Slow (60-90 BPM)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="tempo_medium" value="medium">
                            <label for="tempo_medium">Medium (90-120 BPM)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="tempo_fast" value="fast">
                            <label for="tempo_fast">Fast (120+ BPM)</label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    createDanceabilityFilter() {
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Danceability</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="danceability_low" value="low">
                            <label for="danceability_low">Low Danceability (1-3)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="danceability_medium" value="medium">
                            <label for="danceability_medium">Medium Danceability (4-6)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="danceability_high" value="high">
                            <label for="danceability_high">High Danceability (7-10)</label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    createLyricalThemeFilter() {
        const themes = ['In Love', 'Hopeful Love', 'Breakup', 'Feel Good', 'Motivational', 'Nostalgia', 'Adventure', 'Solitude', 'Celebrating Life', 'Reflection/Introspection'];
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Themes</label>
                    <div class="checkbox-group">
                        ${themes.map(theme => `
                            <div class="checkbox-item">
                                <input type="checkbox" id="theme_${theme.replace(/[^a-zA-Z0-9]/g, '_')}" value="${theme}">
                                <label for="theme_${theme.replace(/[^a-zA-Z0-9]/g, '_')}">${theme}</label>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    createReleaseDateFilter() {
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Release Year Range</label>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <input type="number" id="yearMin" min="1950" max="2024" placeholder="From" style="flex: 1;">
                        <span>-</span>
                        <input type="number" id="yearMax" min="1950" max="2024" placeholder="To" style="flex: 1;">
                    </div>
                </div>
            </div>
        `;
    }
    
    setupArtistAutocomplete() {
        const input = document.getElementById('artistSearchInput');
        const dropdown = document.getElementById('artistDropdown');
        
        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (query.length < 2) {
                dropdown.innerHTML = '';
                dropdown.style.display = 'none';
                return;
            }
            
            const matches = this.availableArtists.filter(artist => 
                artist.toLowerCase().startsWith(query)
            ).slice(0, 10);
            
            if (matches.length > 0) {
                dropdown.innerHTML = matches.map(artist => `
                    <div class="autocomplete-item" data-artist="${artist}">${artist}</div>
                `).join('');
                dropdown.style.display = 'block';
                
                // Add click events to dropdown items
                dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
                    item.addEventListener('click', () => {
                        this.addSelectedArtist(item.dataset.artist);
                        input.value = '';
                        dropdown.style.display = 'none';
                    });
                });
            } else {
                dropdown.style.display = 'none';
            }
        });
        
        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.autocomplete-container')) {
                dropdown.style.display = 'none';
            }
        });
    }
    
    addSelectedArtist(artist) {
        const container = document.getElementById('selectedArtists');
        const existing = container.querySelector(`[data-artist="${artist}"]`);
        if (existing) return;
        
        const item = document.createElement('div');
        item.className = 'selected-item';
        item.dataset.artist = artist;
        item.innerHTML = `
            ${artist}
            <button type="button" class="remove-item" data-artist="${artist}">&times;</button>
        `;
        
        container.appendChild(item);
        
        // Add remove functionality
        item.querySelector('.remove-item').addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeSelectedArtist(artist);
        });
    }
    
    removeSelectedArtist(artist) {
        const item = document.querySelector(`[data-artist="${artist}"]`);
        if (item) {
            item.remove();
        }
    }
    
    getSelectedArtists() {
        const items = document.querySelectorAll('#selectedArtists .selected-item');
        return Array.from(items).map(item => item.dataset.artist);
    }
    
    applyFilter() {
        const filterType = this.currentFilterType;
        let filterValue = {};
        
        switch (filterType) {
            case 'artist':
                const selectedArtists = this.getSelectedArtists();
                if (selectedArtists.length > 0) {
                    filterValue.artists = selectedArtists;
                }
                break;
            case 'genre':
                const genreCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (genreCheckboxes.length > 0) {
                    filterValue.genres = Array.from(genreCheckboxes).map(cb => cb.value);
                }
                break;
            case 'emotion':
                const emotionCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (emotionCheckboxes.length > 0) {
                    filterValue.emotions = Array.from(emotionCheckboxes).map(cb => cb.value);
                }
                break;
            case 'energy':
                const energyCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (energyCheckboxes.length > 0) {
                    const energyLevels = Array.from(energyCheckboxes).map(cb => cb.value);
                    filterValue.energy_levels = energyLevels;
                }
                break;
            case 'tempo':
                const tempoCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (tempoCheckboxes.length > 0) {
                    const tempos = Array.from(tempoCheckboxes).map(cb => cb.value);
                    filterValue.tempo_levels = tempos;
                }
                break;
            case 'danceability':
                const danceabilityCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (danceabilityCheckboxes.length > 0) {
                    const danceabilityLevels = Array.from(danceabilityCheckboxes).map(cb => cb.value);
                    filterValue.danceability_levels = danceabilityLevels;
                }
                break;
            case 'lyrical_theme':
                const themeCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (themeCheckboxes.length > 0) {
                    filterValue.themes = Array.from(themeCheckboxes).map(cb => cb.value);
                }
                break;
            case 'release_date':
                const yearMin = document.getElementById('yearMin').value;
                const yearMax = document.getElementById('yearMax').value;
                if (yearMin || yearMax) {
                    filterValue.year_range = [yearMin ? parseInt(yearMin) : 1950, yearMax ? parseInt(yearMax) : 2024];
                }
                break;
        }
        
        // Update current filters
        this.currentFilters = { ...this.currentFilters, ...filterValue };
        
        // Update filter button appearance
        const filterBtn = document.querySelector(`[data-filter="${filterType}"]`);
        if (Object.keys(filterValue).length > 0) {
            filterBtn.classList.add('active');
        } else {
            filterBtn.classList.remove('active');
        }
        
        this.closeModal();
        
        // Re-perform search (without calling Gemini since only filters changed)
        this.performSearch();
    }
    
    clearCurrentFilter() {
        const filterType = this.currentFilterType;
        
        // Clear the specific filter
        switch (filterType) {
            case 'artist':
                document.getElementById('selectedArtists').innerHTML = '';
                document.getElementById('artistSearchInput').value = '';
                break;
            case 'genre':
            case 'emotion':
            case 'energy':
            case 'tempo':
            case 'danceability':
            case 'lyrical_theme':
                document.querySelectorAll('#modalBody input[type="checkbox"]').forEach(cb => {
                    cb.checked = false;
                });
                break;
            case 'release_date':
                document.getElementById('yearMin').value = '';
                document.getElementById('yearMax').value = '';
                break;
        }
        
        // Remove from current filters
        delete this.currentFilters[filterType];
        
        // Update filter button appearance
        const filterBtn = document.querySelector(`[data-filter="${filterType}"]`);
        filterBtn.classList.remove('active');
    }
    
    clearAllFilters() {
        this.currentFilters = {};
        
        // Remove active class from all filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Reset popularity slider
        document.getElementById('popularitySlider').value = 5;
        
        this.closeModal();
        
        // Re-perform search
        this.performSearch();
    }
    
    closeModal() {
        document.getElementById('filterModal').style.display = 'none';
    }
    
    updatePopularityFilter() {
        const slider = document.getElementById('popularitySlider');
        const value = parseInt(slider.value);
        
        // Update popularity range in filters
        this.currentFilters.popularity_range = [value, 10];
        
        // Re-perform search (without calling Gemini since only filters changed)
        this.performSearch();
    }
    
    updatePlaylistTitle(title) {
        document.getElementById('playlistTitle').textContent = title;
    }
    
    showLoading() {
        document.getElementById('loadingIndicator').style.display = 'flex';
        document.getElementById('noResults').style.display = 'none';
        document.getElementById('tracksList').innerHTML = '';
    }
    
    showError(message) {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('noResults').style.display = 'flex';
        document.getElementById('noResults').querySelector('span').textContent = message;
    }
    
    formatDuration(ms) {
        if (!ms) return '0:00';
        const minutes = Math.floor(ms / 60000);
        const seconds = Math.floor((ms % 60000) / 1000);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    
    setupSearch() {
        // No auto-search on input change - only on Enter key or filter changes
        // This prevents excessive API calls to Gemini
        console.log('Search setup: Gemini will only be called on Enter key press');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VibeAIApp();
});
