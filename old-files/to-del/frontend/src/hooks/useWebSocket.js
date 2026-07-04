import { useEffect, useContext } from 'react';
import io from 'socket.io-client';
import { AppContext } from '../contexts/AppContext';

/**
 * A custom hook to manage the WebSocket connection for the application.
 *
 * This hook initializes a connection to the WebSocket server on component mount,
 * stores the socket instance in the global AppContext, and handles tearing
 * down the connection on component unmount.
 */
export const useWebSocket = () => {
  // Grab the setSocket function from the global context
  const { setSocket } = useContext(AppContext);

  useEffect(() => {
    // Establish connection to the WebSocket server using the URL from environment variables.
    const socketInstance = io(process.env.REACT_APP_WS_URL);

    // Store the socket instance in our global context
    setSocket(socketInstance);

    // --- Register Event Listeners ---

    // Fired upon a successful connection
    socketInstance.on('connect', () => {
      console.log('WebSocket Connected successfully!');
    });

    // Fired when the backend signals a new user conversation has been logged
    socketInstance.on('new_conversation', (data) => {
      console.log('Real-time event: New conversation received.', data);
      // In a full implementation, you would trigger a UI notification here.
      // e.g., using react-toastify: toast.info(`New conversation from ${data.session_id}`);
    });

    // Fired when documents have been uploaded or deleted
    socketInstance.on('documents_updated', () => {
      console.log('Real-time event: Document list has changed.');
      // This is a cue to refetch the document list or show a notification.
    });
    
    // Fired upon disconnection
    socketInstance.on('disconnect', () => {
      console.log('WebSocket Disconnected.');
    });


    // --- Cleanup Function ---
    // This function will be called when the component that uses this hook unmounts.
    return () => {
      // Disconnect the socket to prevent memory leaks and unnecessary connections.
      socketInstance.disconnect();
      // Clear the socket instance from the global state
      setSocket(null);
    };
  }, [setSocket]); // The effect depends on the setSocket function from context.
};

