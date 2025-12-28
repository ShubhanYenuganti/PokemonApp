import { useState } from 'react';
import { authService } from '../services/api';
import './Landing.css';

function Landing() {
  const [loading, setLoading] = useState(false);
  const user = authService.getCurrentUser();

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
        <div className="welcome-card">
          <h2>Welcome to Pokemon Finder!</h2>
          <p>You're now logged in and ready to start your Pokemon journey.</p>
          <div className="user-info">
            <h3>Your Profile</h3>
            <p><strong>Username:</strong> {user?.username}</p>
            {user?.email && <p><strong>Email:</strong> {user.email}</p>}
            {user?.first_name && <p><strong>First Name:</strong> {user.first_name}</p>}
            {user?.last_name && <p><strong>Last Name:</strong> {user.last_name}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Landing;
