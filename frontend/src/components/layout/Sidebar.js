import React from 'react';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Toolbar, 
  Typography, 
  Divider 
} from '@mui/material';
import { NavLink } from 'react-router-dom';

// Icons
import DashboardIcon from '@mui/icons-material/Dashboard';
import ArticleIcon from '@mui/icons-material/Article';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import ChatIcon from '@mui/icons-material/Chat';
import SettingsIcon from '@mui/icons-material/Settings';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber'; // New icon for tickets
import AnalyticsIcon from '@mui/icons-material/Analytics';

const NavItem = ({ to, icon, text }) => (
  <ListItem disablePadding>
    <ListItemButton
      component={NavLink}
      to={to}
      sx={{
        '&.active': {
          backgroundColor: 'primary.main',
          color: 'primary.contrastText',
          '& .MuiListItemIcon-root': {
            color: 'primary.contrastText',
          },
        },
      }}
    >
      <ListItemIcon>{icon}</ListItemIcon>
      <ListItemText primary={text} />
    </ListItemButton>
  </ListItem>
);

const Sidebar = ({ isOpen, onClose }) => {
  const drawerWidth = 240;

  const menuItems = [
    { to: '/dashboard', icon: <DashboardIcon />, text: 'Dashboard' },
    { to: '/documents', icon: <ArticleIcon />, text: 'Documents' },
    { to: '/faqs', icon: <QuestionAnswerIcon />, text: 'FAQs' },
    { to: '/conversations', icon: <ChatIcon />, text: 'Conversations' },
    { to: '/tickets', icon: <ConfirmationNumberIcon />, text: 'Ticket Management' }, // New menu item
        { to: '/configuration', icon: <SettingsIcon />, text: 'Configuration' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Admin Portal
        </Typography>
      </Toolbar>
      
      <Divider />
      
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <NavItem 
              key={item.to} 
              to={item.to} 
              icon={item.icon} 
              text={item.text} 
            />
          ))}
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;