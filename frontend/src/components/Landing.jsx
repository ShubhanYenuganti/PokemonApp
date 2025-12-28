import { useState, useEffect } from 'react';
import { authService, pokemonService } from '../services/api';
import './Landing.css';

function Landing() {
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [fetchMessage, setFetchMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selectedPokemon, setSelectedPokemon] = useState(null);
  const [modalPosition, setModalPosition] = useState({ x: 100, y: 100 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [leftPanelWidth, setLeftPanelWidth] = useState(33.33); // 1/3 of the screen
  const [isResizing, setIsResizing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadsList, setUploadsList] = useState([]);
  const [defaultsList, setDefaultsList] = useState([]);
  const [uploadsPage, setUploadsPage] = useState(1);
  const [defaultsPage, setDefaultsPage] = useState(1);
  const [uploadsTotalPages, setUploadsTotalPages] = useState(1);
  const [defaultsTotalPages, setDefaultsTotalPages] = useState(1);
  const [loadingUploads, setLoadingUploads] = useState(false);
  const [loadingDefaults, setLoadingDefaults] = useState(false);
  const [uploadsCount, setUploadsCount] = useState(0);
  const [defaultsCount, setDefaultsCount] = useState(0);
  const user = authService.getCurrentUser();

  useEffect(() => {
    loadUploads(1);
    loadDefaults(1);
  }, []);

  const loadUploads = async (page) => {
    setLoadingUploads(true);
    try {
      const response = await pokemonService.getAll(page, 'CSV');
      setUploadsList(response.results || []);
      setUploadsPage(page);
      setUploadsCount(response.count || 0);
      // Calculate total pages based on count and page size
      setUploadsTotalPages(Math.ceil((response.count || 0) / 10));
    } catch (err) {
      console.error('Load uploads error:', err);
      setUploadsList([]);
    } finally {
      setLoadingUploads(false);
    }
  };

  const loadDefaults = async (page) => {
    setLoadingDefaults(true);
    try {
      const response = await pokemonService.getAll(page, 'API');
      setDefaultsList(response.results || []);
      setDefaultsPage(page);
      setDefaultsCount(response.count || 0);
      // Calculate total pages based on count and page size
      setDefaultsTotalPages(Math.ceil((response.count || 0) / 10));
    } catch (err) {
      console.error('Load defaults error:', err);
      setDefaultsList([]);
    } finally {
      setLoadingDefaults(false);
    }
  };

  const handleFetchPokemon = async () => {
    setFetching(true);
    setFetchMessage('');
    try {
      const response = await pokemonService.fetchFromApi();
      setFetchMessage(response.message || 'Pokemon fetched successfully!');
      // Refresh the defaults list
      loadDefaults(1);
    } catch (err) {
      console.error('Fetch error:', err);
      setFetchMessage('Error fetching Pokemon: ' + (err.response?.data?.error || err.message));
    } finally {
      setFetching(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await authService.logout();
      // Reload the page to trigger re-render and show login screen
      window.location.reload();
    } catch (err) {
      console.error('Logout error:', err);
      // Even if logout fails, clear local storage and reload
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const results = await pokemonService.search(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error('Search error:', err);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handlePokemonClick = (pokemon) => {
    setSelectedPokemon(pokemon);
  };

  const handleToggleFavorite = async () => {
    if (!selectedPokemon) return;
    
    try {
      await pokemonService.toggleFavorite(selectedPokemon.id);
      // Update the local state
      const updatedPokemon = { ...selectedPokemon, is_favorite: !selectedPokemon.is_favorite };
      setSelectedPokemon(updatedPokemon);
      // Update in search results if present
      setSearchResults(searchResults.map(p => 
        p.id === selectedPokemon.id ? updatedPokemon : p
      ));
    } catch (err) {
      console.error('Toggle favorite error:', err);
      alert('Error toggling favorite: ' + (err.response?.data?.error || err.message));
    }
  };

  const closeModal = () => {
    setSelectedPokemon(null);
  };

  const handleDeletePokemon = async () => {
    if (!selectedPokemon) return;
    
    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${selectedPokemon.name}? This action cannot be undone.`
    );
    
    if (!confirmDelete) return;

    try {
      await pokemonService.delete(selectedPokemon.id);
      // Remove from search results if present
      setSearchResults(searchResults.filter(p => p.id !== selectedPokemon.id));
      // Close modal
      setSelectedPokemon(null);
      // Show success message (could add a notification state)
      alert(`${selectedPokemon.name} has been deleted successfully`);
    } catch (err) {
      console.error('Delete error:', err);
      alert('Error deleting Pokemon: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleMouseDown = (e) => {
    if (e.target.classList.contains('modal-header') || e.target.closest('.modal-header')) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - modalPosition.x,
        y: e.clientY - modalPosition.y
      });
      e.preventDefault();
    }
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        setModalPosition({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y
        });
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragStart]);

  useEffect(() => {
    const handleResizeMove = (e) => {
      if (isResizing) {
        const newWidth = (e.clientX / window.innerWidth) * 100;
        // Limit between 20% and 80%
        if (newWidth >= 20 && newWidth <= 80) {
          setLeftPanelWidth(newWidth);
        }
      }
    };

    const handleResizeEnd = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMove);
      document.addEventListener('mouseup', handleResizeEnd);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleResizeMove);
      document.removeEventListener('mouseup', handleResizeEnd);
    };
  }, [isResizing]);

  const handleResizeStart = () => {
    setIsResizing(true);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setUploadMessage('');
      } else {
        setUploadMessage('Please select a valid CSV file');
        setSelectedFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage('Please select a CSV file first');
      return;
    }

    setUploading(true);
    setUploadMessage('');
    try {
      const response = await pokemonService.uploadCsv(selectedFile);
      setUploadMessage(response.message || 'Pokemon uploaded successfully!');
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.getElementById('csv-file-input');
      if (fileInput) fileInput.value = '';
      // Refresh the uploads list
      loadUploads(1);
    } catch (err) {
      console.error('Upload error:', err);
      setUploadMessage('Error uploading CSV: ' + (err.response?.data?.error || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="landing-container">
      <nav className="navbar">
        <div className="navbar-content">
          <h1 className="navbar-title">Pokemon Finder</h1>
          <div className="navbar-user">
            <span className="welcome-text">
              Welcome, {user?.username || 'User'}!
            </span>
            <button 
              onClick={handleLogout} 
              className="logout-button"
              disabled={loading}
            >
              {loading ? 'Logging out...' : 'Logout'}
            </button>
          </div>
        </div>
      </nav>

      <div className="landing-content">
        <div className="split-container">
          <div className="left-panel" style={{ width: `${leftPanelWidth}%` }}>
            <div className="upload-section">
              <h3>Upload Pokemon</h3>
              <div className="upload-container">
                <input
                  id="csv-file-input"
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="file-input"
                />
                <button
                  onClick={handleUpload}
                  className="upload-button"
                  disabled={uploading || !selectedFile}
                >
                  {uploading ? 'Uploading...' : 'Upload CSV'}
                </button>
              </div>
              {selectedFile && (
                <div className="selected-file">
                  Selected: {selectedFile.name}
                </div>
              )}
              {uploadMessage && (
                <div className={`upload-message ${uploadMessage.includes('Error') || uploadMessage.includes('select') ? 'error' : 'success'}`}>
                  {uploadMessage}
                </div>
              )}
            </div>

            <div className="search-section">
              <h3>Search Pokemon</h3>
              <div className="search-container">
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search Pokemon by name, type, or category... (Press Enter to search)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                />
                {searching && <div className="search-loading">Searching...</div>}
              </div>
              
              {searchResults.length > 0 && (
                <div className="search-results">
                  <h4>Results ({searchResults.length}):</h4>
                  <ul className="pokemon-list">
                    {searchResults.map((pokemon) => (
                      <li 
                        key={pokemon.id} 
                        className="pokemon-item"
                        onClick={() => handlePokemonClick(pokemon)}
                      >
                        <div className="pokemon-info">
                          {pokemon.sprite && (
                            <img 
                              src={pokemon.sprite} 
                              alt={pokemon.name} 
                              className="pokemon-sprite"
                            />
                          )}
                          <div className="pokemon-details">
                            <span className="pokemon-name">{pokemon.name}</span>
                            <span className="pokemon-types">
                              {pokemon.type_primary}
                              {pokemon.type_secondary && ` / ${pokemon.type_secondary}`}
                            </span>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {searchQuery && searchResults.length === 0 && !searching && (
                <div className="no-results">
                  No Pokemon found matching "{searchQuery}"
                </div>
              )}
            </div>

            <div className="pokemon-lists-section">
              <h3>All Pokemon</h3>
              
              {/* Uploads Section */}
              <div className="pokemon-section">
                <h4>Uploaded: CSV ({uploadsCount})</h4>
                {loadingUploads ? (
                  <div className="loading-text">Loading uploads...</div>
                ) : uploadsList.length > 0 ? (
                  <>
                    <ul className="pokemon-list">
                      {uploadsList.map((pokemon) => (
                        <li 
                          key={pokemon.id} 
                          className="pokemon-item"
                          onClick={() => handlePokemonClick(pokemon)}
                        >
                          <div className="pokemon-info">
                            {pokemon.sprite && (
                              <img 
                                src={pokemon.sprite} 
                                alt={pokemon.name} 
                                className="pokemon-sprite"
                              />
                            )}
                            <div className="pokemon-details">
                              <span className="pokemon-name">{pokemon.name}</span>
                              <span className="pokemon-types">
                                {pokemon.type_primary}
                                {pokemon.type_secondary && ` / ${pokemon.type_secondary}`}
                              </span>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                    {uploadsTotalPages > 1 && (
                      <div className="pagination">
                        <button 
                          onClick={() => loadUploads(uploadsPage - 1)}
                          disabled={uploadsPage === 1}
                          className="pagination-button"
                        >
                          Previous
                        </button>
                        <span className="pagination-info">
                          Page {uploadsPage} of {uploadsTotalPages}
                        </span>
                        <button 
                          onClick={() => loadUploads(uploadsPage + 1)}
                          disabled={uploadsPage === uploadsTotalPages}
                          className="pagination-button"
                        >
                          Next
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="no-results">No uploaded Pokemon yet</div>
                )}
              </div>

              {/* Defaults Section */}
              <div className="pokemon-section">
                <h4>Uploaded: API ({defaultsCount})</h4>
                {loadingDefaults ? (
                  <div className="loading-text">Loading defaults...</div>
                ) : defaultsList.length > 0 ? (
                  <>
                    <ul className="pokemon-list">
                      {defaultsList.map((pokemon) => (
                        <li 
                          key={pokemon.id} 
                          className="pokemon-item"
                          onClick={() => handlePokemonClick(pokemon)}
                        >
                          <div className="pokemon-info">
                            {pokemon.sprite && (
                              <img 
                                src={pokemon.sprite} 
                                alt={pokemon.name} 
                                className="pokemon-sprite"
                              />
                            )}
                            <div className="pokemon-details">
                              <span className="pokemon-name">{pokemon.name}</span>
                              <span className="pokemon-types">
                                {pokemon.type_primary}
                                {pokemon.type_secondary && ` / ${pokemon.type_secondary}`}
                              </span>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                    {defaultsTotalPages > 1 && (
                      <div className="pagination">
                        <button 
                          onClick={() => loadDefaults(defaultsPage - 1)}
                          disabled={defaultsPage === 1}
                          className="pagination-button"
                        >
                          Previous
                        </button>
                        <span className="pagination-info">
                          Page {defaultsPage} of {defaultsTotalPages}
                        </span>
                        <button 
                          onClick={() => loadDefaults(defaultsPage + 1)}
                          disabled={defaultsPage === defaultsTotalPages}
                          className="pagination-button"
                        >
                          Next
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="no-results">No default Pokemon yet</div>
                )}
              </div>
            </div>
          </div>

          <div className="resizer" onMouseDown={handleResizeStart}></div>

          <div className="right-panel" style={{ width: `${100 - leftPanelWidth}%` }}>
            <div className="map-placeholder">
              <p>Map will be displayed here</p>
            </div>
          </div>
        </div>
      </div>

      {selectedPokemon && (
        <div 
          className="modal-overlay" 
          onClick={closeModal}
        >
          <div 
            className="pokemon-modal" 
            style={{
              left: `${modalPosition.x}px`,
              top: `${modalPosition.y}px`
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div 
              className="modal-header"
              onMouseDown={handleMouseDown}
            >
              <h2>{selectedPokemon.name}</h2>
              <div className="modal-header-actions">
                <button 
                  className="favorite-button" 
                  onClick={handleToggleFavorite}
                  title={selectedPokemon.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                  {selectedPokemon.is_favorite ? '❤️' : '🤍'}
                </button>
                <button className="close-button" onClick={closeModal}>×</button>
              </div>
            </div>
            
            <div className="modal-content">
              {selectedPokemon.sprite && (
                <img 
                  src={selectedPokemon.sprite} 
                  alt={selectedPokemon.name} 
                  className="modal-sprite"
                />
              )}
              
              <div className="modal-section">
                <h3>Basic Info</h3>
                <p><strong>ID:</strong> {selectedPokemon.id}</p>
                <p><strong>Category:</strong> {selectedPokemon.category}</p>
                <p><strong>Height:</strong> {selectedPokemon.height / 10}m</p>
                <p><strong>Weight:</strong> {selectedPokemon.weight / 10}kg</p>
                <p><strong>Source:</strong> {selectedPokemon.source}</p>
              </div>

              <div className="modal-section">
                <h3>Types</h3>
                <div className="type-badges">
                  <span className="type-badge">{selectedPokemon.type_primary}</span>
                  {selectedPokemon.type_secondary && (
                    <span className="type-badge">{selectedPokemon.type_secondary}</span>
                  )}
                </div>
              </div>

              <div className="modal-section">
                <h3>Abilities</h3>
                <div className="abilities-list">
                  {selectedPokemon.abilities && selectedPokemon.abilities.map((ability, idx) => (
                    <span key={idx} className="ability-badge">{ability}</span>
                  ))}
                </div>
              </div>

              <div className="modal-section">
                <h3>Stats</h3>
                {selectedPokemon.stats && (
                  <div className="stats-grid">
                    {Object.entries(selectedPokemon.stats).map(([key, value]) => (
                      <div key={key} className="stat-row">
                        <span className="stat-name">{key}:</span>
                        <span className="stat-value">{value}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="modal-section">
                <h3>Moves</h3>
                <div className="moves-list">
                  {selectedPokemon.moves && [...new Set(selectedPokemon.moves)].map((move, idx) => (
                    <span key={idx} className="move-badge">{move}</span>
                  ))}
                </div>
              </div>

              {(selectedPokemon.latitude && selectedPokemon.longitude) && (
                <div className="modal-section">
                  <h3>Location</h3>
                  <p><strong>Coordinates:</strong> {selectedPokemon.latitude.toFixed(6)}, {selectedPokemon.longitude.toFixed(6)}</p>
                  {selectedPokemon.location_name && (
                    <p><strong>Name:</strong> {selectedPokemon.location_name}</p>
                  )}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="delete-button" onClick={handleDeletePokemon}>
                Delete Pokemon
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Landing;
