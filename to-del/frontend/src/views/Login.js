import React, { useContext, useEffect } from 'react';
import { Container, Paper, Typography, CircularProgress } from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

/**
 * Auto-login component for development.
 * This component will automatically log in the user and redirect to the dashboard.
 */
const Login = () => {
  const { user, login } = useContext(AuthContext);

  // Automatically log in the user when the component mounts
  useEffect(() => {
    if (!user) {
      login({ email: 'admin@example.com', name: 'Admin User' });
    }
  }, [login, user]);

  // If the user is logged in, navigate to the dashboard.
  if (user) {
    return <Navigate to="/" replace />;
  }

  // Display a loading indicator while the automatic login is in process
  return (
    <Container component="main" maxWidth="xs">
      <Paper
        elevation={6}
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: 4,
          justifyContent: 'center',
          height: 300,
        }}
      >
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Redirecting to dashboard...</Typography>
      </Paper>
    </Container>
  );
};

export default Login;