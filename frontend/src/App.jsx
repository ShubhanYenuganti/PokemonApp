import { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Landing from './components/Landing';
import { authService, pokemonService } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [allPokemon, setAllPokemon] = useState([]);
  const [loadingPokemon, setLoadingPokemon] = useState(false);

  useEffect(() => {
    // Check if user is already authenticated
    const authenticated = authService.isAuthenticated();
    setIsAuthenticated(authenticated);
    
    // If already authenticated, fetch Pokemon
    if (authenticated) {
      fetchPokemon();
    }
  }, []);

  const fetchPokemon = async () => {
    setLoadingPokemon(true);
    try {
      let pokemon = await pokemonService.getAllForMap();
      
      // If no Pokemon exist, fetch from API first
      if (pokemon.length === 0) {
        console.log('No Pokemon found, fetching from PokeAPI...');
        await pokemonService.fetchFromApi();
        // Then get the newly fetched Pokemon
        pokemon = await pokemonService.getAllForMap();
      }
      
      setAllPokemon(pokemon);
    } catch (err) {
      console.error('Error fetching Pokemon:', err);
      setAllPokemon([]);
    } finally {
      setLoadingPokemon(false);
    }
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    fetchPokemon();
  };

  const handleRegisterSuccess = () => {
    setIsAuthenticated(true);
    fetchPokemon();
  };

  const switchToRegister = () => {
    setShowRegister(true);
  };

  const switchToLogin = () => {
    setShowRegister(false);
  };

  if (isAuthenticated) {
    return <Landing allPokemon={allPokemon} loadingPokemon={loadingPokemon} onPokemonUpdate={fetchPokemon} />;
  }

  if (showRegister) {
    return (
      <Register 
        onRegisterSuccess={handleRegisterSuccess}
        onSwitchToLogin={switchToLogin}
      />
    );
  }

  return (
    <Login 
      onLoginSuccess={handleLoginSuccess}
      onSwitchToRegister={switchToRegister}
    />
  );
}

export default App;
