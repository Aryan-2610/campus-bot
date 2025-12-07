import React, { useState } from 'react';
import { Box, CssBaseline, Toolbar } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';

const drawerWidth = 240;

/**
 * The main layout component that wraps the entire admin portal.
 * It includes the Header, Sidebar, and the main content area.
 *
 * @param {object} props - The component props.
 * @param {React.ReactNode} props.children - The page content to be rendered within the layout.
 */
const Layout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Header 
        drawerWidth={drawerWidth} 
        handleDrawerToggle={handleDrawerToggle} 
      />
      <Sidebar
        drawerWidth={drawerWidth}
        mobileOpen={mobileOpen}
        handleDrawerToggle={handleDrawerToggle}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: (theme) => theme.palette.grey[100],
          minHeight: '100vh'
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;

