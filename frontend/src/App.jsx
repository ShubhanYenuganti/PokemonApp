import { useState, useEffect } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Landing from './components/Landing';
import { authService } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    // Check if user is already authenticated
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleRegisterSuccess = () => {
    setIsAuthenticated(true);
  };

  const switchToRegister = () => {
    setShowRegister(true);
  };

  const switchToLogin = () => {
    setShowRegister(false);
  };

  if (isAuthenticated) {
    return <Landing />;
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
