import React, { createContext, useState } from 'react';

// Create the context
export const AppContext = createContext(null);

/**
 * Provides global state for the application, such as the WebSocket instance.
 * Theme management has been removed to enforce a single, professional UI.
 */
export const AppProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);

  // The value provided to all consuming components
  const contextValue = {
    socket,
    setSocket,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};