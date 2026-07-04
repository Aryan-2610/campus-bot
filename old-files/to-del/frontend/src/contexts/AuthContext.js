import React, { createContext, useState, useEffect, useCallback } from 'react';

// Create the context with a default null value.
export const AuthContext = createContext(null);

/**
 * Provides authentication state (user, login, logout) to the entire application.
 * It persists the user session in localStorage.
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // Start in a loading state

  // On initial application load, try to load the user from localStorage.
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        setUser(JSON.parse(savedUser));
      }
    } catch (error) {
      console.error("Failed to parse user from localStorage", error);
      localStorage.removeItem('user');
    } finally {
      setLoading(false); // Finished loading user from storage
    }
  }, []); // Empty dependency array means this runs only once on mount

  // Logs the user in by saving their data to state and localStorage.
  const login = useCallback((userData) => {
    try {
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    } catch (error) {
      console.error("Failed to save user to localStorage", error);
    }
  }, []);

  // Logs the user out by clearing their data from state and localStorage.
  const logout = useCallback(() => {
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  // The value provided to consuming components.
  const contextValue = { user, login, logout, loading };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};