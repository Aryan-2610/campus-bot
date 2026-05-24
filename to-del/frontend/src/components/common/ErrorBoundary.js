import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

/**
 * A React Error Boundary component.
 * It catches JavaScript errors in its child component tree, logs them,
 * and displays a fallback UI instead of the crashed component tree.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  /**
   * This lifecycle method is invoked after an error has been thrown by a descendant component.
   * It receives the error that was thrown as a parameter and should return a value to update state.
   * @param {Error} error - The error that was thrown.
   * @returns {object} An object to update state.
   */
  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  /**
   * This lifecycle method is invoked after an error has been thrown by a descendant component.
   * It receives two parameters: the error and information about which component threw the error.
   * @param {Error} error - The error that was thrown.
   * @param {object} errorInfo - An object with a componentStack key containing information about which component threw the error.
   */
  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service like Sentry or LogRocket
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // Render the custom fallback UI
      return (
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: '100vh', 
            p: 4,
            backgroundColor: 'grey.100'
          }}
        >
          <Paper sx={{ p: 4, maxWidth: '600px', textAlign: 'center', boxShadow: 6 }}>
            <ErrorOutlineIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h5" component="h1" gutterBottom>
              Something Went Wrong
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              We've encountered an unexpected issue. Please try refreshing the page. If the problem persists, please contact support.
            </Typography>
            <Button 
              variant="contained" 
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </Button>

            {/* Display detailed error info only in development mode for easier debugging */}
            {process.env.NODE_ENV === 'development' && (
              <Box 
                sx={{ 
                  mt: 3, 
                  textAlign: 'left', 
                  p: 2, 
                  backgroundColor: '#fbe9e7', 
                  borderRadius: 1, 
                  maxHeight: 250, 
                  overflowY: 'auto',
                  border: '1px solid',
                  borderColor: 'error.light'
                }}
              >
                <Typography variant="subtitle2" color="error.dark" gutterBottom>
                  {this.state.error && this.state.error.toString()}
                </Typography>
                <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.75rem', color: 'error.dark' }}>
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      );
    }

    // If there's no error, render children as normal
    return this.props.children;
  }
}

export default ErrorBoundary;

