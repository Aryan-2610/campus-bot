import { createTheme } from '@mui/material/styles';

// A professional, minimalist color palette inspired by government portals.
const palette = {
  primary: {
    main: '#0d47a1', // A deep, official blue
    light: '#5472d3',
    dark: '#002171',
    contrastText: '#ffffff',
  },
  background: {
    default: '#f7f9fc', // A very light, clean gray
    paper: '#ffffff',   // White for all card and paper elements
  },
  text: {
    primary: '#212121',   // Dark gray for high contrast and readability
    secondary: '#616161', // Lighter gray for secondary text
  },
  divider: '#e0e0e0',    // A light border color
  action: {
    active: '#0d47a1', // Ensure active elements like icons use the primary blue
  },
};

// Common settings for the theme
const themeSettings = {
  palette: palette,
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2rem', fontWeight: 600 },
    h2: { fontSize: '1.75rem', fontWeight: 600 },
    h3: { fontSize: '1.5rem', fontWeight: 600 },
    h4: { fontSize: '1.25rem', fontWeight: 600 },
    h5: { fontSize: '1.1rem', fontWeight: 600 },
    h6: { fontSize: '1rem', fontWeight: 600 },
  },
  shape: {
    borderRadius: 6, // A slightly less rounded, more professional corner radius
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none', // Important: disables MUI's default gradient
          // Use a subtle border instead of a heavy shadow for a flatter look
          boxShadow: 'none',
          border: `1px solid ${palette.divider}`,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          // A white header with a simple bottom border
          backgroundColor: palette.background.paper,
          color: palette.text.primary,
          borderBottom: `1px solid ${palette.divider}`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          // Ensure the sidebar has a right-side border for clear separation
          borderRight: `1px solid ${palette.divider}`,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          // Make table headers slightly bolder and a bit lighter in color
          fontWeight: 600,
          color: palette.text.secondary,
          backgroundColor: '#fafafa',
        },
      },
    },
  },
};

// Create and export the single, final theme
export const professionalTheme = createTheme(themeSettings);