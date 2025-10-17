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
        this.availableLanguages = [];
        this.isAgenticSearch = true;
        this.hasUnsavedChanges = false;
        this.isHomeView = true;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadDefaultPlaylists();
        this.loadAvailableArtists();
        this.loadAvailableLanguages();
    }
    
    bindEvents() {
        // Home logo click
        document.getElementById('homeLogo').addEventListener('click', () => {
            this.returnToHome();
        });
        
        // Search input
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', () => {
            this.markAsNeedsUpdate();
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
        
        // Search home button
        document.getElementById('searchHomeBtn').addEventListener('click', () => {
            this.returnToHome();
        });
        
        // Add filters button
        document.getElementById('addFiltersBtn').addEventListener('click', () => {
            this.toggleFilters();
        });
        
        // Search update button
        document.getElementById('searchUpdateBtn').addEventListener('click', () => {
                this.performSearch();
        });
        
        // Action buttons (removed - no longer needed)
        
        // Search chips (removed - no longer needed)
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.openFilterModal(e.currentTarget.dataset.filter);
            });
        });
        
        // Clear all filters button
        document.getElementById('clearAllFilters').addEventListener('click', () => {
            this.clearAllFilters();
        });
        
        // Spotify playlist creation button
        document.getElementById('createSpotifyPlaylistBtn').addEventListener('click', () => {
            this.createSpotifyPlaylist();
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
        
        // Close modal on outside click
        document.getElementById('filterModal').addEventListener('click', (e) => {
            if (e.target.id === 'filterModal') {
                this.closeModal();
            }
        });
    }
    
    toggleFilters() {
        const filterRow = document.getElementById('filterButtonsRow');
        const addFiltersBtn = document.getElementById('addFiltersBtn');
        
        if (filterRow.style.display === 'none' || filterRow.style.display === '') {
            // Show filters
            filterRow.style.display = 'flex';
            addFiltersBtn.classList.add('active');
            addFiltersBtn.innerHTML = '<i class="fas fa-minus"></i> Hide Filters';
            } else {
            // Hide filters
            filterRow.style.display = 'none';
            addFiltersBtn.classList.remove('active');
            addFiltersBtn.innerHTML = '<i class="fas fa-plus"></i> Add Filters';
        }
    }
    
    updateFilters() {
        // Update filters based on current UI state
        this.markAsNeedsUpdate();
    }
    
    markAsNeedsUpdate() {
        const searchBtn = document.getElementById('searchUpdateBtn');
        searchBtn.classList.add('needs-update');
    }
    
    clearNeedsUpdate() {
        const searchBtn = document.getElementById('searchUpdateBtn');
        searchBtn.classList.remove('needs-update');
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
            case 'language':
                content = this.createLanguageFilter();
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
    
    createLanguageFilter() {
        return `
            <div class="filter-options">
                <div class="filter-option">
                    <label>Select Languages</label>
                    <div class="checkbox-group">
                        ${this.availableLanguages.map(language => `
                            <div class="checkbox-item">
                                <input type="checkbox" id="language_${language.replace(/[^a-zA-Z0-9]/g, '_')}" value="${language}">
                                <label for="language_${language.replace(/[^a-zA-Z0-9]/g, '_')}">${language}</label>
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
            case 'language':
                const languageCheckboxes = document.querySelectorAll('#modalBody input[type="checkbox"]:checked');
                if (languageCheckboxes.length > 0) {
                    filterValue.languages = Array.from(languageCheckboxes).map(cb => cb.value);
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
        
        // Mark as needing update instead of auto-searching
        this.markAsNeedsUpdate();
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
        
        this.closeModal();
        
        // Mark as needing update instead of auto-searching
        this.markAsNeedsUpdate();
    }
    
    closeModal() {
        document.getElementById('filterModal').style.display = 'none';
    }
    
    async loadAvailableArtists() {
        try {
            const response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/v2/api/artists');
            const data = await response.json();
            if (data.success) {
                this.availableArtists = data.artists;
            }
        } catch (error) {
            console.error('Error loading artists:', error);
        }
    }
    
    async loadAvailableLanguages() {
        try {
            const response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/v2/api/languages');
            const data = await response.json();
            if (data.success) {
                this.availableLanguages = data.languages;
            }
        } catch (error) {
            console.error('Error loading languages:', error);
        }
    }
    
    async loadDefaultPlaylists() {
        try {
            console.log('Loading default playlists...');
            const response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/v2/api/playlists');
            const data = await response.json();
            
            console.log('Playlists response:', data);
            
            if (data.success) {
                this.renderDefaultPlaylists(data.playlists);
            } else {
                console.warn('Playlists API not available yet, using fallback');
                this.renderFallbackPlaylists();
            }
        } catch (error) {
            console.error('Error loading playlists:', error);
            console.warn('Using fallback playlists due to backend error');
            this.renderFallbackPlaylists();
        }
    }
    
    renderFallbackPlaylists() {
        console.log('Rendering fallback playlists');
        const container = document.getElementById('playlistButtons');
        if (!container) return;
        
        container.innerHTML = `
            <div style="color: #888; font-size: 12px; padding: 10px; text-align: center;">
                <i class="fas fa-music"></i><br>
                Ready-to-go playlists<br>
                <small>Loading...</small>
            </div>
        `;
    }
    
    renderDefaultPlaylists(playlists) {
        console.log('Rendering playlists:', playlists);
        const container = document.getElementById('playlistButtons');
        console.log('Container found:', container);
        container.innerHTML = '';
        
        // Convert object to array of playlists
        const playlistArray = Object.entries(playlists).map(([id, playlist]) => ({
            id,
            ...playlist
        }));
        
        console.log('Playlist array:', playlistArray);
        
        playlistArray.forEach(playlist => {
            const btn = document.createElement('button');
            btn.className = 'playlist-btn';
            btn.innerHTML = `
                <i class="fas fa-music"></i>
                <div>
                    <div style="font-weight: 600; margin-bottom: 4px;">${playlist.name}</div>
                    <div style="font-size: 11px; color: #888;">${playlist.description}</div>
                </div>
            `;
            btn.addEventListener('click', () => {
                console.log('🎵 Playlist button clicked:', playlist.name);
                this.loadPlaylistWithFilters(playlist);
            });
            container.appendChild(btn);
        });
        
        console.log('Playlist buttons added:', container.children.length);
    }
    
    async loadPlaylistWithFilters(playlist) {
        console.log('🎵 Loading playlist:', playlist);
        
        try {
            // Show results page immediately
            this.showResults();
            this.clearError();
            this.showLoading();
            
            // Set the search input with the playlist query
            document.getElementById('searchInput').value = playlist.query || playlist.name;
            this.lastNaturalQuery = playlist.query || playlist.name;
            
            // Apply the playlist's filters
            this.currentFilters = playlist.filters || {};
            console.log('🔧 Applied filters:', this.currentFilters);
            
            // Perform search with the playlist's query and filters
            const response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/v2/api/agentic-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: playlist.query || playlist.name,
                    filters: this.currentFilters,
                    max_results: 50
                })
            });
            
            console.log('📡 API Response status:', response.status);
            const data = await response.json();
            console.log('📊 API Response data:', data);
            console.log('🎵 data.success:', data.success);
            console.log('🎵 data.songs:', data.songs);
            console.log('🎵 data.songs length:', data.songs?.length);
            
            if (data.success) {
                this.currentPlaylist = playlist;
                this.currentSongs = data.songs;
                console.log('🎯 About to call renderSongs with:', data.songs?.length, 'songs');
                this.renderSongs(data.songs, data);
                this.updatePlaylistTitle('Your Curated Playlist');
                this.showReturnButton();
                this.clearNeedsUpdate();
            } else {
                console.log('❌ API returned success: false');
                this.renderSongs([], data);
            }
        } catch (error) {
            console.error('Error loading playlist:', error);
            this.renderSongs([], null);
        }
    }
    
    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }
        
        // Show results page immediately
        this.showResults();
        this.clearError();
        this.showLoading();
        
        try {
            // Check if natural language query changed
            const naturalQueryChanged = query !== this.lastNaturalQuery;
            this.lastNaturalQuery = query;
            
            let response;
            
            if (this.isAgenticSearch && query) {
                // Use agentic search
                response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/v2/api/agentic-search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        filters: this.currentFilters,
                        max_results: 10
                    })
                });
            } else {
                // Use regular search
                response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/v2/api/search', {
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
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSongs = data.songs;
                this.renderSongs(data.songs, data);
                this.updatePlaylistTitle('Your Curated Playlist');
                this.clearNeedsUpdate();
            } else {
                this.renderSongs([], data);
            }
        } catch (error) {
            console.error('Error performing search:', error);
            // Don't show error message - just show no results
            this.renderSongs([], null);
        }
    }
    
    async surpriseMe() {
        const surpriseQueries = [
            'surprise me with something new',
            'random songs I might like',
            'discover something unexpected',
            'play something different',
            'surprise me'
        ];
        
        const randomQuery = surpriseQueries[Math.floor(Math.random() * surpriseQueries.length)];
        document.getElementById('searchInput').value = randomQuery;
        this.lastNaturalQuery = randomQuery;
        this.performSearch();
    }
    
    renderSongs(songs, searchData = null) {
        console.log('🎵 renderSongs called with:', songs?.length, 'songs');
        console.log('🎵 Songs data:', songs);
        console.log('🔍 Call stack:', new Error().stack);
        
        const container = document.getElementById('tracksList');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const noResults = document.getElementById('noResults');
        
        console.log('🔍 DOM elements found:', {
            container: !!container,
            loadingIndicator: !!loadingIndicator,
            noResults: !!noResults
        });
        
        // Hide loading indicator
        loadingIndicator.style.display = 'none';
        
        // Check if we have songs
        if (!songs || songs.length === 0) {
            console.log('❌ No songs found - showing no results');
            noResults.style.display = 'flex';
            container.innerHTML = '';
            return;
        }
        
        console.log('✅ Rendering', songs.length, 'songs');
        
        // Hide no results message
        noResults.style.display = 'none';
        
        // Generate HTML for songs
        const html = songs.map((song, index) => `
            <div class="track-item" data-index="${index}">
                <div class="track-info">
                    <div class="track-title">${song.title || 'Unknown Title'}</div>
                    <div class="track-artist">${song.artist || 'Unknown Artist'}</div>
                    <div class="track-album">${song.album || 'Unknown Album'}</div>
                </div>
                <div class="track-meta">
                    <i class="fas fa-heart track-heart"></i>
                </div>
            </div>
        `).join('');
        
        console.log('📝 Generated HTML length:', html.length);
        
        // Set the HTML content
        container.innerHTML = html;
        
        console.log('🎯 Container updated, innerHTML length:', container.innerHTML.length);
        
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
    
    showResults() {
        this.isHomeView = false;
        document.getElementById('resultsSection').style.display = 'block';
        this.showReturnButton();
        
        // Add results-view class to main content
        document.querySelector('.main-content').classList.add('results-view');
        
        // Hide home page elements but keep search bar visible
        document.querySelector('.main-header').style.display = 'none';
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }
    
    showReturnButton() {
        document.getElementById('searchHome').style.display = 'block';
    }
    
    hideReturnButton() {
        document.getElementById('searchHome').style.display = 'none';
    }
    
    returnToHome() {
        this.isHomeView = true;
        document.getElementById('resultsSection').style.display = 'none';
        this.hideReturnButton();
        
        // Remove results-view class from main content
        document.querySelector('.main-content').classList.remove('results-view');
        
        // Show home page elements
        document.querySelector('.main-header').style.display = 'block';
        
        // Reset filter button state
        const filterRow = document.getElementById('filterButtonsRow');
        const addFiltersBtn = document.getElementById('addFiltersBtn');
        filterRow.style.display = 'none';
        addFiltersBtn.classList.remove('active');
        addFiltersBtn.innerHTML = '<i class="fas fa-plus"></i> Add Filters';
        
        // Clear search input
        document.getElementById('searchInput').value = '';
        this.lastNaturalQuery = '';
        
        // Clear filters
        this.currentFilters = {};
        this.resetFiltersUI();
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    resetFiltersUI() {
        // Reset dropdowns
        document.querySelectorAll('.dropdown-text').forEach(text => {
            text.textContent = 'Any';
        });
        
        // Reset toggles
        document.querySelectorAll('.toggle-switch').forEach(toggle => {
            toggle.classList.remove('active');
        });
        
        // Reset checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Set familiar tracks as default (if element exists)
        const familiarCheck = document.getElementById('familiarCheck');
        const familiarToggle = document.getElementById('familiarToggle');
        if (familiarCheck) {
            familiarCheck.checked = true;
        }
        if (familiarToggle) {
            familiarToggle.classList.add('active');
        }
        
        // Reset sliders (if elements exist)
        const energySlider = document.getElementById('energySlider');
        const tempoSlider = document.getElementById('tempoSlider');
        if (energySlider) {
            energySlider.value = 5;
        }
        if (tempoSlider) {
            tempoSlider.value = 5;
        }
    }
    
    updatePlaylistTitle(title) {
        document.getElementById('playlistTitle').textContent = title;
    }
    
    showLoading() {
        document.getElementById('loadingIndicator').style.display = 'flex';
        document.getElementById('noResults').style.display = 'none';
        document.getElementById('tracksList').innerHTML = '';
    }
    
    clearError() {
        document.getElementById('noResults').style.display = 'none';
        document.getElementById('loadingIndicator').style.display = 'none';
    }
    
    showError(message) {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('noResults').style.display = 'flex';
        document.getElementById('noResults').querySelector('span').textContent = message;
    }
    
    async createSpotifyPlaylist() {
        if (!this.currentSongs || this.currentSongs.length === 0) {
            this.showError('No songs to create playlist with');
            return;
        }
        
        const createBtn = document.getElementById('createSpotifyPlaylistBtn');
        const originalText = createBtn.innerHTML;
        
        try {
            // Show loading state
            createBtn.disabled = true;
            createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
            
            // Get playlist name from current search
            const playlistTitle = document.getElementById('playlistTitle').textContent;
            const playlistName = playlistTitle === 'Search Results' ? 'VibeAI Search Results' : playlistTitle;
            
            // Create playlist
            const response = await fetch('https://vibeai-backend-534228867297.us-west1.run.app/create-spotify-playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    songs: this.currentSongs.slice(0, 20), // Limit to 20 songs
                    playlist_name: playlistName
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Show success message and open playlist
                this.showSuccess(`Playlist created with ${data.tracks_added} songs!`);
                
                // Open Spotify playlist in new tab
                window.open(data.playlist_url, '_blank');
                
                // Update button to show success
                createBtn.innerHTML = '<i class="fab fa-spotify"></i> View Playlist';
                createBtn.onclick = () => window.open(data.playlist_url, '_blank');
            } else {
                this.showError(`Failed to create playlist: ${data.error}`);
            }
            
        } catch (error) {
            console.error('Error creating Spotify playlist:', error);
            this.showError('Failed to create Spotify playlist');
        } finally {
            // Reset button state
            setTimeout(() => {
                createBtn.disabled = false;
                createBtn.innerHTML = originalText;
                createBtn.onclick = () => this.createSpotifyPlaylist();
            }, 3000);
        }
    }
    
    showSuccess(message) {
        // Create a temporary success notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #1db954, #1ed760);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = `✅ ${message}`;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    markAsNeedsUpdate() {
        this.hasUnsavedChanges = true;
        const createBtn = document.getElementById('createPlaylistBtn');
        if (createBtn) {
            createBtn.style.background = 'linear-gradient(135deg, #ff6b6b, #ff5252)';
            createBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Search';
        }
    }
    
    clearNeedsUpdate() {
        this.hasUnsavedChanges = false;
        const createBtn = document.getElementById('createPlaylistBtn');
        if (createBtn) {
            createBtn.style.background = 'linear-gradient(135deg, #00ff88, #00cc6a)';
            createBtn.innerHTML = '<i class="fas fa-plus"></i> Create Playlist';
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VibeAIApp();
});