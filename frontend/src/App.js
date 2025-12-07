import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box, CircularProgress } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// --- Professional Theme ---
import { professionalTheme } from './styles/theme';
// -------------------------

// Contexts
import { AuthContext } from './contexts/AuthContext';

// Layout and Views
import Layout from './components/layout/Layout';
import Login from './views/Login';
import Dashboard from './views/Dashboard';
import DocumentManagement from './views/DocumentManagement';
import FAQManagement from './views/FAQManagement';
import ConversationLogs from './views/ConversationLogs';
import TicketManagement from './views/TicketManagement'; // New
import Analytics from './views/Analytics';
import BotConfiguration from './views/BotConfiguration';

// Global CSS
import './App.css';

/**
 * Wrapper for protected routes.
 * Shows spinner while loading, redirects if no user,
 * and wraps Layout around nested routes.
 */
const ProtectedRoutes = () => {
  const { user, loading } = useContext(AuthContext);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

function App() {
  return (
    <ThemeProvider theme={professionalTheme}>
      <CssBaseline />
      <ToastContainer
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        theme="light"
      />
      <Router>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<Login />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoutes />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/documents" element={<DocumentManagement />} />
            <Route path="/faqs" element={<FAQManagement />} />
            <Route path="/conversations" element={<ConversationLogs />} />
            <Route path="/tickets" element={<TicketManagement />} />  {/* New */}
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/configuration" element={<BotConfiguration />} />

            {/* Redirect unknown paths */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
